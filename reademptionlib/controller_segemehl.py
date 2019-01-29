import concurrent.futures
import os
import sys
from reademptionlib.helpers import Helpers
from reademptionlib.paths import Paths
from reademptionlib.bammerger import BamMerger
from reademptionlib.crossalignfilter import CrossAlignFilter
from reademptionlib.fasta import FastaParser
from reademptionlib.segemehl import Segemehl
from reademptionlib.readalignerstatstable import ReadAlignerStatsTable
from reademptionlib.rawstatdata import RawStatDataWriter, RawStatDataReader
from reademptionlib.readalignerstats import ReadAlignerStats
from reademptionlib.readprocessor import ReadProcessor
from reademptionlib.readrealigner import ReadRealigner
from reademptionlib.sambamconverter import SamToBamConverter


class SegemehlController():

    def __init__(self, args):
        self._args = args
        self._paths = Paths(args)
        self._helpers = Helpers(args)

    def align_with_segemehl(self):
        """Perform the alignment of the reads."""
        self._test_folder_existance(
            self._paths.required_read_alignment_folders())
        assert self._args.paired_end in [True, False]
        self._ref_seq_files = self._paths.get_ref_seq_files()
        self._paths.set_ref_seq_paths(self._ref_seq_files)
        self._test_align_file_existance()
        if not self._args.paired_end:
            # Single end reads
            self._read_files = self._paths.get_read_files()
            self._lib_names = self._paths.get_lib_names_single_end()
            self._paths.set_read_files_dep_file_lists_single_end(
                self._read_files, self._lib_names)
            if not self._args.realign:
                self._set_primary_aligner_paths_to_final_paths()
            self._prepare_reads_single_end()
            self._align_single_end_reads()
        else:
            # Paired end reads
            self._read_file_pairs = self._paths.get_read_file_pairs()
            self._lib_names = self._paths.get_lib_names_paired_end()
            self._paths.set_read_files_dep_file_lists_paired_end(
                self._read_file_pairs, self._lib_names)
            if not self._args.realign:
                self._set_primary_aligner_paths_to_final_paths()
            self._prepare_reads_paired_end()
            self._align_paired_end_reads()
        self._sam_to_bam(
            self._paths.primary_read_aligner_sam_paths,
            self._paths.primary_read_aligner_bam_prefix_paths,
            self._paths.primary_read_aligner_bam_paths)
        self._generate_read_alignment_stats(
            self._lib_names,
            self._paths.primary_read_aligner_bam_paths,
            self._paths.unaligned_reads_paths,
            self._paths.primary_read_aligner_stats_path)
        final_unaligned_reads_paths = self._paths.unaligned_reads_paths
        if self._args.realign:
            self._run_realigner_and_process_alignments()
            self._merge_bam_files()
            final_unaligned_reads_paths = (
                self._paths.realigned_unaligned_reads_paths)
        if self._args.crossalign_cleaning_str is not None:
            self._remove_crossaligned_reads()
        self._generate_read_alignment_stats(
            self._lib_names,
            self._paths.read_alignment_bam_paths,
            final_unaligned_reads_paths,
            self._paths.read_alignments_stats_path)
        self._write_alignment_stat_table()

    def _remove_crossaligned_reads(self):
        self._string_to_species_and_sequence_ids()
        jobs = []
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for (bam_path, bam_with_crossmappings_path,
                 bam_cleaned_tmp_path, crossmapped_reads_path) in zip(
                    self._paths.read_alignment_bam_paths,
                    self._paths.read_alignment_bam_with_crossmappings_paths,
                    self._paths.read_alignment_bam_cross_cleaned_tmp_paths,
                    self._paths.crossmapped_reads_paths):
                jobs.append(executor.submit(
                    self._remove_crossaligned_reads_for_lib, bam_path,
                    bam_with_crossmappings_path, bam_cleaned_tmp_path,
                    crossmapped_reads_path))
        # Evaluate thread outcome
        self._check_job_completeness(jobs)

    def _remove_crossaligned_reads_for_lib(
            self, bam_path, bam_with_crossmappings_path, bam_cleaned_tmp_path,
            crossmapped_reads_path):
        # Perform the removal or cross aligned reads
        cross_align_filter = CrossAlignFilter(
            bam_path, bam_cleaned_tmp_path, crossmapped_reads_path,
            self._species_and_sequence_ids)
        cross_align_filter.determine_crossmapped_reads()
        cross_align_filter.write_crossmapping_free_bam()
        # Rename the original mapping file that potentially
        # contains cross aligned reads
        os.rename(bam_path, bam_with_crossmappings_path)
        os.rename(bam_path + ".bai", bam_with_crossmappings_path + ".bai")
        # Move the cross aligned filtered file to the final mapping
        # path
        os.rename(bam_cleaned_tmp_path, bam_path)
        os.rename(bam_cleaned_tmp_path + ".bai", bam_path + ".bai")

    def _string_to_species_and_sequence_ids(self):
        self._species_and_sequence_ids = {}
        orgs_and_seq_ids_strs = self._args.crossalign_cleaning_str.split(";")
        if len(orgs_and_seq_ids_strs) < 2:
            self._write_err_msg_and_quit(
                "Error! Only one organism is defined for the cross align "
                "removal. This does not make sense.\nYou gave the "
                "following input:\n%s\n" % self._args.crossalign_cleaning_str)
        for org_and_seq_ids_str in orgs_and_seq_ids_strs:
            org, seq_ids_str = org_and_seq_ids_str.strip().split(":")
            seq_ids = [seq_id.strip() for seq_id in seq_ids_str.split(",")]
            if "" in seq_ids:
                seq_ids.remove("")
            if len(seq_ids) < 1:
                self._write_err_msg_and_quit(
                    "Error! No sequence ID was given for the species '%s'. "
                    "This does not make sense.\nYou gave the "
                    "following input:\n%s\n" % (
                        org, self._args.crossalign_cleaning_str))
            self._species_and_sequence_ids[org] = seq_ids

    def _set_primary_aligner_paths_to_final_paths(self):
        # If no remapping is performed the paths of the final bam files
        # is the paths of the primary mapper
        self._paths.primary_read_aligner_bam_prefix_paths = (
            self._paths.read_alignment_bam_prefix_paths)
        self._paths.primary_read_aligner_bam_paths = (
            self._paths.read_alignment_bam_paths)
        self._paths.primary_read_aligner_stats_path = (
            self._paths.read_alignments_stats_path)

    def _merge_bam_files(self):
        jobs = []
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for merged_bam, primary_aligner_bam, realigner_bam in zip(
                    self._paths.read_alignment_bam_paths,
                    self._paths.primary_read_aligner_bam_paths,
                    self._paths.read_realigner_bam_paths):
                bam_merger = BamMerger()
                jobs.append(executor.submit(
                    bam_merger.merge, merged_bam,
                    primary_aligner_bam, realigner_bam))
        self._check_job_completeness(jobs)
        if not self._args.keep_original_alignments:
            for bam_file_list in [
                    self._paths.primary_read_aligner_bam_paths,
                    self._paths.read_realigner_bam_paths]:
                for bam_file in bam_file_list:
                    os.remove(bam_file)
                    os.remove("%s.bai" % bam_file)

    def _run_realigner_and_process_alignments(self):
        # As the realigner needs a *sorted* SAM file
        self._generate_sorted_tmp_sam_file()
        self._realign_unmapped_reads()
        self._sam_to_bam(
            self._paths.read_realigner_sam_paths,
            self._paths.read_realigner_bam_prefixes_paths,
            self._paths.read_realigner_sam_paths)
        self._generate_read_alignment_stats(
            self._lib_names,
            self._paths.read_realigner_bam_paths,
            self._paths.realigned_unaligned_reads_paths,
            self._paths.read_realigner_stats_path)

    def _test_align_file_existance(self):
        """Test if the input file for the the align subcommand exist."""
        if len(self._paths.get_read_files()) == 0:
            self._write_err_msg_and_quit("Error! No read libraries given!\n")
        if len(self._ref_seq_files) == 0:
            self._write_err_msg_and_quit(
                "Error! No reference sequence files given!\n")

    def _test_folder_existance(self, task_specific_folders):
        """Test the existance of required folders."""
        for folder in (
                self._paths.required_base_folders() + task_specific_folders):
            if not os.path.exists(folder):
                self._write_err_msg_and_quit(
                    "Error! Folder '%s' does not exist! Is the given project "
                    "folder name correct?\n" % folder)

    def _file_needs_to_be_created(self, file_path, quiet=False):
        """Test if a file exists of need to be created."""
        if not self._args.check_for_existing_files:
            return True
        if os.path.exists(file_path):
            if not quiet:
                sys.stderr.write(
                    "File %s exists. Skipping its generation.\n" % file_path)
            return False
        return True

    def _prepare_reads_single_end(self):
        """Manage the prepartion of reads before the actual mappings."""
        read_files_and_jobs = {}
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for lib_name, read_path, processed_read_path in zip(
                    self._lib_names, self._paths.read_paths,
                    self._paths.processed_read_paths):
                if not self._file_needs_to_be_created(
                        processed_read_path):
                    continue
                read_processor = ReadProcessor(
                    poly_a_clipping=self._args.poly_a_clipping,
                    min_read_length=self._args.min_read_length,
                    fastq=self._args.fastq,
                    min_phred_score=self._args.min_phred_score,
                    adapter=self._args.adapter,
                    reverse_complement=self._args.reverse_complement)
                read_files_and_jobs[lib_name] = executor.submit(
                    read_processor.process_single_end, read_path,
                    processed_read_path)
        self._evaluet_job_and_generate_stat_file(read_files_and_jobs)

    def _prepare_reads_paired_end(self):
        read_files_and_jobs = {}
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for lib_name, read_path_pair, processed_read_path_pair in zip(
                self._lib_names, self._paths.read_path_pairs,
                    self._paths.processed_read_path_pairs):
                for processed_read_path in processed_read_path_pair:
                    if not self._file_needs_to_be_created(
                            processed_read_path):
                        continue
                    read_processor = ReadProcessor(
                        poly_a_clipping=False,
                        min_read_length=self._args.min_read_length,
                        fastq=self._args.fastq,
                        min_phred_score=self._args.min_phred_score,
                        adapter=self._args.adapter)
                read_files_and_jobs[lib_name] = executor.submit(
                    read_processor.process_paired_end, read_path_pair,
                    processed_read_path_pair)
        self._evaluet_job_and_generate_stat_file(read_files_and_jobs)

    def _evaluet_job_and_generate_stat_file(self, read_files_and_jobs):
        raw_stat_data_writer = RawStatDataWriter(pretty=True)
        # Evaluate thread outcome
        self._check_job_completeness(read_files_and_jobs.values())
        if not self._file_needs_to_be_created(
                self._paths.read_processing_stats_path):
            return
        # Create a dict of the read file names and the processing
        # counting results
        read_files_and_stats = dict(
            [(lib_name, job.result()) for lib_name, job in
             read_files_and_jobs.items()])
        raw_stat_data_writer.write(
            read_files_and_stats, self._paths.read_processing_stats_path)

    def _align_single_end_reads(self):
        """Manage the actual alignment of single end reads."""
        read_aligner = Segemehl(
            self._args.segemehl_bin, self._args.progress)
        if self._file_needs_to_be_created(self._paths.index_path):
            read_aligner.build_index(
                self._paths.ref_seq_paths, self._paths.index_path)
        for read_path, output_path, nomatch_path, bam_path in zip(
            self._paths.processed_read_paths,
            self._paths.primary_read_aligner_sam_paths,
            self._paths.unaligned_reads_paths,
                self._paths.read_alignment_bam_paths):
            if not self._file_needs_to_be_created(output_path):
                continue
            elif not self._file_needs_to_be_created(bam_path):
                continue
            read_aligner.run_alignment(
                read_path, self._paths.index_path, self._paths.ref_seq_paths,
                output_path, nomatch_path, int(self._args.processes),
                int(self._args.segemehl_accuracy),
                float(self._args.segemehl_evalue), self._args.split,
                paired_end=False)

    def _align_paired_end_reads(self):
        """Manage the actual alignemnt of paired end reads."""
        read_aligner = Segemehl(
            self._args.segemehl_bin, self._args.progress)
        if self._file_needs_to_be_created(self._paths.index_path):
            read_aligner.build_index(
                self._paths.ref_seq_paths, self._paths.index_path)
        for read_path_pair, output_path, nomatch_path, bam_path in zip(
            self._paths.processed_read_path_pairs,
            self._paths.primary_read_aligner_sam_paths,
            self._paths.unaligned_reads_paths,
                self._paths.primary_read_aligner_bam_paths):
            if not self._file_needs_to_be_created(output_path):
                continue
            elif not self._file_needs_to_be_created(bam_path):
                continue
            read_aligner.run_alignment(
                read_path_pair, self._paths.index_path,
                self._paths.ref_seq_paths, output_path, nomatch_path,
                int(self._args.processes), int(self._args.segemehl_accuracy),
                float(self._args.segemehl_evalue), self._args.split,
                paired_end=True)

    def _realign_unmapped_reads(self):
        read_realigner = ReadRealigner(
            self._args.lack_bin, self._args.progress)
        for (query_fasta_path, query_sam_path, realignment_sam_path,
             unaligned_reads_path) in zip(
                self._paths.unaligned_reads_paths,
                self._paths.read_realigner_tmp_sam_paths,
                self._paths.read_realigner_sam_paths,
                self._paths.realigned_unaligned_reads_paths):
            read_realigner.run_alignment(
                query_fasta_path, query_sam_path, self._paths.ref_seq_paths,
                realignment_sam_path, unaligned_reads_path,
                int(self._args.processes), int(self._args.segemehl_accuracy))
            os.remove(query_sam_path)

    def _sam_to_bam(self, sam_paths, bam_prefixes_paths, bam_paths):
        """Manage the conversion of mapped read from SAM to BAM format."""
        sam_to_bam_converter = SamToBamConverter()
        jobs = []
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for sam_path, bam_prefix_path, bam_path in zip(
                    sam_paths, bam_prefixes_paths, bam_paths):
                if not self._file_needs_to_be_created(bam_path):
                    continue
                jobs.append(executor.submit(
                    sam_to_bam_converter.sam_to_bam,
                    sam_path, bam_prefix_path))
        # Evaluate thread outcome
        self._check_job_completeness(jobs)

    def _generate_sorted_tmp_sam_file(self):
        sam_to_bam_converter = SamToBamConverter()
        jobs = []
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for bam_path, sam_path in zip(
                    self._paths.primary_read_aligner_bam_paths,
                    self._paths.read_realigner_tmp_sam_paths):
                jobs.append(executor.submit(
                    sam_to_bam_converter.bam_to_sam, bam_path, sam_path))
        # Evaluate thread outcome
        self._check_job_completeness(jobs)

    def _generate_read_alignment_stats(
            self, lib_names, result_bam_paths, unaligned_reads_paths,
            output_stats_path):
        """Manage the generation of alingment statistics."""
        raw_stat_data_writer = RawStatDataWriter(pretty=True)
        read_files_and_jobs = {}
        if not self._file_needs_to_be_created(output_stats_path):
            return
        with concurrent.futures.ProcessPoolExecutor(
                max_workers=self._args.processes) as executor:
            for (lib_name, read_alignment_bam_path,
                 unaligned_reads_path) in zip(
                    lib_names, result_bam_paths, unaligned_reads_paths):
                read_aligner_stats = ReadAlignerStats()
                read_files_and_jobs[lib_name] = executor.submit(
                    read_aligner_stats.count, read_alignment_bam_path,
                    unaligned_reads_path)
        # Evaluate thread outcome
        self._check_job_completeness(read_files_and_jobs.values())
        read_files_and_stats = dict(
            [(lib_name, job.result())
             for lib_name, job in read_files_and_jobs.items()])
        raw_stat_data_writer.write(read_files_and_stats, output_stats_path)

    def _write_alignment_stat_table(self):
        """Manage the creation of the mapping statistic output table."""
        raw_stat_data_reader = RawStatDataReader()
        read_processing_stats = raw_stat_data_reader.read(
            self._paths.read_processing_stats_path)
        final_alignment_stats = raw_stat_data_reader.read(
            self._paths.read_alignments_stats_path)
        realignment_stats = None
        primary_aligner_stats = None
        if self._args.realign:
            primary_aligner_stats = raw_stat_data_reader.read(
                self._paths.primary_read_aligner_stats_path)
            realignment_stats = raw_stat_data_reader.read(
                self._paths.read_realigner_stats_path)
        read_aligner_stats_table = ReadAlignerStatsTable(
            read_processing_stats, final_alignment_stats,
            primary_aligner_stats,
            realignment_stats, self._lib_names,
            self._paths.read_alignment_stats_table_path, self._args.paired_end)
        read_aligner_stats_table.write()

    def _ref_ids_to_file(self, ref_seq_paths):
        """Translate the reference ID to file paths."""
        ref_ids_to_file = {}
        fasta_parser = FastaParser()
        for ref_seq_path in ref_seq_paths:
            ref_seq_file = os.path.basename(ref_seq_path)
            with open(ref_seq_path) as ref_seq_fh:
                ref_seq_id = fasta_parser.header_id(
                    fasta_parser.single_entry_file_header(ref_seq_fh))
                ref_ids_to_file[ref_seq_id] = ref_seq_file
            return ref_ids_to_file
