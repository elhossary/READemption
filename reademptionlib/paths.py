import os
import shutil
import sys


class Paths(object):

    def __init__(self, args):
        self.base_path = args.project_path
        self._set_folder_names()
        self._set_static_files()
        
    def _set_folder_names(self):
        """Set the name of folders used in a project."""
        self.input_folder = "%s/input" % (self.base_path)
        self.output_folder = "%s/output" % (self.base_path)
        self._set_input_folder_names()
        self._set_read_processing_folder_names()
        self._set_read_alignment_folder_names()
        self._set_coverage_folder_names()
        self._set_gene_quanti_folder_names()
        self._set_deseq2_folder_names()
        self._set_vis_align_folder_names()
        self._set_vis_gene_quanti_folder_names()
        self._set_vis_deseq2_folder_names()

    def _set_input_folder_names(self):
        self.read_fasta_folder = "%s/reads" % self.input_folder
        self.ref_seq_folder = "%s/reference_sequences" % self.input_folder
        self.annotation_folder = "%s/annotations" % self.input_folder

    def _set_read_processing_folder_names(self):
        self.read_processing_base_folder = "{}/processed_reads".format(
            self.output_folder)
        self.read_processing_report_folder = "{}/reports_and_stats".format(
            self.read_processing_base_folder)

    def _set_read_alignment_folder_names(self):
        self.align_base_folder = "%s/align" % self.output_folder
        self.read_alignment_index_folder = "%s/index" % (
            self.align_base_folder)
        self.read_alignments_folder = "%s/alignments" % (
            self.align_base_folder)
        self.unaligned_reads_folder = "%s/unaligned_reads" % (
            self.align_base_folder)
        self.align_report_folder = "%s/reports_and_stats" % (
            self.align_base_folder)
        self.raw_stat_data_folder = "%s/stats_data_json" % (
            self.align_report_folder)

    def _set_coverage_folder_names(self):
        self.coverage_base_folder = "%s/coverage" % self.output_folder
        self.coverage_raw_folder = "%s/coverage-raw" % self.coverage_base_folder
        self.coverage_tnoar_min_norm_folder = "%s/coverage-tnoar_min_normalized" % (
            self.coverage_base_folder)
        self.coverage_tnoar_mil_norm_folder = "%s/coverage-tnoar_mil_normalized" % (
            self.coverage_base_folder)

    def _set_gene_quanti_folder_names(self):
        self.gene_quanti_base_folder = (
            "%s/gene_quanti" % self.output_folder)
        self.gene_quanti_per_lib_folder = "%s/gene_quanti_per_lib" % (
            self.gene_quanti_base_folder)
        self.gene_quanti_combined_folder = "%s/gene_quanti_combined" % (
            self.gene_quanti_base_folder)
        self.gene_wise_quanti_combined_path = (
            "%s/gene_wise_quantifications_combined.csv" %
            self.gene_quanti_combined_folder)
        self.gene_wise_quanti_combined_rpkm_path = (
            "%s/gene_wise_quantifications_combined_rpkm.csv" %
            self.gene_quanti_combined_folder)
        self.gene_wise_quanti_combined_tnoar_path = (
            "%s/gene_wise_quantifications_combined_tnoar.csv" %
            self.gene_quanti_combined_folder)

    def _set_deseq2_folder_names(self):
        self.deseq2_base_folder = ("%s/DESeq2" % self.output_folder)
        self.deseq2_raw_folder = ("%s/DESeq2_raw" % self.deseq2_base_folder)
        self.deseq2_extended_folder = (
            "%s/DESeq2_with_annotations" % self.deseq2_base_folder)

    def _set_vis_align_folder_names(self):
        self.vis_align_base_folder = (
            "%s/vis_align" % self.output_folder)

    def _set_vis_gene_quanti_folder_names(self):
        self.vis_gene_quanti_base_folder = (
            "%s/vis_gene_quanti" % self.output_folder)

    def _set_vis_deseq2_folder_names(self):
        self.vis_deseq2_base_folder = (
            "%s/vis_deseq2" % self.output_folder)
        self.vis_deseq2_scatter_plot_path = (
            "%s/MA_plots.pdf" %
            self.vis_deseq2_base_folder)
        self.vis_deseq2_volcano_plot_path = (
            "%s/volcano_plots_log2_fold_change_vs_p-value.pdf" %
            self.vis_deseq2_base_folder)
        self.vis_deseq2_volcano_plot_adj_path = (
            "%s/volcano_plots_log2_fold_change_vs_adjusted_p-value.pdf" %
            self.vis_deseq2_base_folder)

    def _set_static_files(self):
        """Set name of common files."""
        self.read_processing_stats_path = "%s/read_processing.json" % (
            self.raw_stat_data_folder)
        self.primary_read_aligner_stats_path = (
            "%s/read_alignments_primary_aligner.json" % (
                self.raw_stat_data_folder))
        self.read_realigner_stats_path = "%s/read_alignments_realigner.json" % (
            self.raw_stat_data_folder)
        self.read_alignments_stats_path = "%s/read_alignments_final.json" % (
            self.raw_stat_data_folder)
        self.read_file_stats = "%s/input_read_stats.txt" % (
            self.align_report_folder)
        self.ref_seq_file_stats = "%s/reference_sequences_stats.txt" % (
            self.align_report_folder)
        self.read_alignment_stats_table_path = "%s/read_alignment_stats.csv" % (
            self.align_report_folder)
        self.index_path = "%s/index.idx" % self.read_alignment_index_folder
        self.index_path_star = "%s/chrLength.txt" % self.read_alignment_index_folder
        self.deseq2_script_path = "%s/deseq2.R" % self.deseq2_raw_folder
        self.deseq2_pca_heatmap_path = "%s/sample_comparison_pca_heatmap.pdf" % (
            self.deseq2_raw_folder)
        self.deseq2_tmp_session_info_script = "%s/tmp.R" % self.deseq2_raw_folder
        self.deseq2_session_info = "%s/R_session_info.txt" % (
            self.deseq2_raw_folder)
        self.version_path = "%s/version_log.txt" % (
            self.output_folder)

    def _get_sorted_folder_content(self, folder):
        """Return the sorted file list of a folder"""
        return list(filter(lambda file:
                           not (file.endswith("~") or
                                os.path.basename(file).startswith(".")),
                           sorted(os.listdir(folder))))

    def get_read_files(self):
        """Read the names of the read files."""
        return self._get_sorted_folder_content(self.read_fasta_folder)

    def get_read_file_pairs(self):
        """Read the names of the read files as paired for paired end reads."""
        read_files = self._get_sorted_folder_content(self.read_fasta_folder)
        if len(read_files) % 2 != 0:
            sys.stderr.write(
                "Error: Number of files is unequal. This cannot be "
                "the case for paired end run data.\n")
            sys.exit(1)
        for read_file in read_files:
            if not ("_p1" in read_file or "_p2" in read_file):
                sys.stderr.write(
                    "Error: You specified this as paired end run data but the "
                    "file name '%s' does not contain '_p1' or '_p2'.\n")
                sys.exit(1)
        read_file_pairs = list(read_file_pair for read_file_pair in
                               zip(read_files[::2], read_files[1::2]))
        for read_file_pair in read_file_pairs:
            if read_file_pair[0] != read_file_pair[1].replace("_p2.", "_p1."):
                sys.stderr.write("Error: Cannot detect pairs of paired end "
                                 "sequenceing files. Please check that file "
                                 "names contain '_p1' and '_p2'.\n")
                sys.exit(1)
        return read_file_pairs

    def get_lib_names_single_end(self):
        """Extract the suffux free name of single end libraries"""
        return [self._clean_file_name(file_name)
                for file_name in self.get_read_files()]

    def get_lib_names_paired_end(self):
        """Extract the suffux free name of paired end libraries

        For each pair of read files one library name is returned.

        """
        p1_names = [self._clean_file_name(file_name)
                    for file_name in self.get_read_files()][::2]
        for p1_name in p1_names:
            if not p1_name.endswith("_p1"):
                sys.stderr.write("Error: File '%s' should end with '_p1' but "
                                 "does not. Please check file name convention "
                                 "for paired end reads.\n" % p1_name)
                sys.exit(1)
        return [p1_name[:-3] for p1_name in p1_names]

    def _clean_file_name(self, file_name):
        for suffix in ["bz2", "BZ", "gz", "GZ", "fa", "fasta", "FA", "FASTA",
                       "fastq", "fq", "FQ", "FASTQ"]:
            if file_name.endswith(suffix):
                suffix = "." + suffix
                file_name = file_name[:-len(suffix)]
        return file_name

    def get_ref_seq_files(self):
        """Read the names of reference sequence files."""
        return self._get_sorted_folder_content(self.ref_seq_folder)

    def get_annotation_files(self):
        """Read the names of annotation files."""
        return self._get_sorted_folder_content(self.annotation_folder)

    def get_alignment_files(self):
        """Read the names of STAR output files in order to alter them"""
        return self._get_sorted_folder_content(self.read_alignments_folder)

    def required_folders(self):
        return (self.required_base_folders() +
                self.required_input_folders() +
                self.required_read_processing_folders() +
                self.required_read_alignment_folders() +
                self.required_coverage_folders() +
                self.required_gene_quanti_folders() +
                self.required_deseq2_folders() +
                self.required_vis_align_folders() +
                self.required_vis_gene_quanti_folders() +
                self.required_vis_deseq2_folders())

    def required_base_folders(self):
        return [self.input_folder, self.output_folder]

    def required_input_folders(self):
        return [self.read_fasta_folder, self.ref_seq_folder,
                self.annotation_folder]

    def required_read_processing_folders(self):
        return [self.read_processing_base_folder,
                self.read_processing_report_folder]
    
    def required_read_alignment_folders(self):
        return [self.align_base_folder, self.read_alignments_folder,
                self.unaligned_reads_folder,
                self.read_alignment_index_folder,
                self.align_report_folder,
                self.raw_stat_data_folder]

    def required_coverage_folders(self):
        return [self.coverage_base_folder, self.coverage_raw_folder,
                self.coverage_tnoar_min_norm_folder,
                self.coverage_tnoar_mil_norm_folder]

    def required_gene_quanti_folders(self):
        return [self.gene_quanti_base_folder, self.gene_quanti_per_lib_folder,
                self.gene_quanti_combined_folder]

    def required_deseq2_folders(self):
        return [self.deseq2_base_folder, self.deseq2_raw_folder,
                self.deseq2_extended_folder]

    def required_vis_align_folders(self):
        return [self.vis_align_base_folder]

    def required_vis_gene_quanti_folders(self):
        return [self.vis_gene_quanti_base_folder]

    def required_vis_deseq2_folders(self):
        return [self.vis_deseq2_base_folder]

    def set_read_files_dep_file_lists_single_end(self, read_files, lib_names):
        self.read_paths = self._path_list(self.read_fasta_folder, read_files)
        self.processed_read_paths = self._path_list(
            self.read_processing_base_folder, lib_names,
            appendix="_processed.fa.gz")
        self.unaligned_reads_paths = self._path_list(
            self.unaligned_reads_folder, lib_names,
            appendix="_unaligned.fa")
        self.realigned_unaligned_reads_paths = self._path_list(
            self.unaligned_reads_folder, lib_names,
            appendix="_unaligned_after_realignment.fa")
        self._set_alignment_paths(lib_names)

    def set_read_files_dep_file_lists_paired_end(
            self, read_file_pairs, lib_names):
        self.read_path_pairs = [
            self._path_list(self.read_fasta_folder, read_file_pair)
            for read_file_pair in read_file_pairs]
        self.processed_read_path_pairs = [
            self._path_list(                
                self.read_processing_base_folder,
                [self._clean_file_name(read_file)
                 for read_file in read_file_pair], appendix="_processed.fa.gz")
            for read_file_pair in read_file_pairs]
        # The read of both files that are not matchend will be dumped
        # together into on file. Due to this there is only one file
        # per pair.
        self.unaligned_reads_paths = self._path_list(
            self.unaligned_reads_folder, lib_names,
            appendix="_unaligned.fa")
        self.realigned_unaligned_reads_paths = self._path_list(
            self.unaligned_reads_folder, lib_names,
            appendix="_unaligned_after_realignment.fa")
        self._set_alignment_paths(lib_names)

    def _set_alignment_paths(self, lib_names):
        ###
        # For the primary mapper
        self.primary_read_aligner_sam_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_primary_aligner.sam")
        self.primary_read_aligner_bam_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_primary_aligner.bam")
        # samtool appends ".bam" so only the prefix is required
        self.primary_read_aligner_bam_prefix_paths = self._path_list(
            self.read_alignments_folder,
            lib_names, appendix="_alignments_primary_aligner")
        ###
        # For the remapper
        self.read_realigner_tmp_sam_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_tmp_for_realigner.sam")
        self.read_realigner_sam_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_realigner.sam")
        self.read_realigner_bam_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_realigner.bam")
        self.read_realigner_bam_prefixes_paths = self._path_list(
            self.read_alignments_folder,
            lib_names, appendix="_alignments_realigner")
        ###
        # For the cross-aligned cleaned
        self.read_alignment_bam_cross_cleaned_tmp_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_tmp_crossmapped_cleaned.bam")
        self.read_alignment_bam_with_crossmappings_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_potententially_with_crossmappings.bam")
        self.crossmapped_reads_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_crossmapped_reads.txt")
        ###
        # For the final (merged) version
        self.read_alignment_bam_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_final.bam")
        self.read_alignment_bam_prefix_paths = self._path_list(
            self.read_alignments_folder, lib_names,
            appendix="_alignments_final")

    def set_ref_seq_paths(self, ref_seq_files):
        self.ref_seq_paths = self._path_list(
            self.ref_seq_folder, ref_seq_files)

    def set_annotation_paths(self, annotation_files):
        self.annotation_paths = self._path_list(
            self.annotation_folder, annotation_files)

    def _path_list(self, folder, files, appendix=""):
        return ["%s/%s%s" % (folder, file, appendix) for file in files]

    def gene_quanti_path(self, read_file, annotation_file):
        return "%s/%s_to_%s.csv" % (
            self.gene_quanti_per_lib_folder, read_file, annotation_file)

    def wiggle_file_raw_path(self, read_file, strand, multi=None, div=None):
        return self._wiggle_file_path(
            self.coverage_raw_folder, read_file, strand, multi=None, div=None)

    def wiggle_file_tnoar_norm_min_path(
            self, read_file, strand, multi=None, div=None):
        return self._wiggle_file_path(
            self.coverage_tnoar_min_norm_folder, read_file, strand, multi, div)

    def wiggle_file_tnoar_norm_mil_path(
            self, read_file, strand, multi=None, div=None):
        return self._wiggle_file_path(
            self.coverage_tnoar_mil_norm_folder, read_file, strand, multi, div)

    def _wiggle_file_path(
            self, folder, read_file, strand, multi=None, div=None):
        path = "%s/%s" % (folder, read_file)
        if div is not None:
            path += "_div_by_%.1f" % (div)
        if multi is not None:
            path += "_multi_by_%.1f" % (multi)
        path += "_%s.wig" % strand
        return path

    def get_processed_read_files(self):
            """Read the names of processed read files"""
            return self._get_sorted_folder_content(
                self.read_processing_base_folder)

    def get_primary_alignment(self):
        """Read the names of primary aligned sam files"""
        return self._get_sorted_folder_content(self.read_alignments_folder)

    def relocate_and_rename_star_output_se(self):
        star_log_file = "{}/Log.out".format(os.getcwd())
        if os.path.exists(star_log_file):
            shutil.move(star_log_file,
                        "{}/STAR_Log.out".format(self.align_report_folder))
        align_output = self.read_alignments_folder
        for output_file in os.listdir(align_output):
            change_align_output = output_file.replace(
                ".samAligned.out.sam", ".sam")
            if change_align_output != output_file:
                os.rename("{}/{}".format(align_output, output_file),
                          "{}/{}".format(align_output, change_align_output))
            if output_file.endswith('Unmapped.out.mate1'):
                change_unmapped_output = output_file.replace(
                    "alignments_primary_aligner.samUnmapped.out.mate1",
                    "unaligned.fa")
                if change_unmapped_output != output_file:
                    os.rename("{}/{}".format(align_output, output_file),
                              "{}/{}".format(self.unaligned_reads_folder,
                                             change_unmapped_output))
            report_output = self.align_report_folder
            suffix_list = [".out", "SJ.out.tab"]
            for suffix in suffix_list:
                if output_file.endswith(suffix):
                    shutil.move("{}/{}".format(
                        align_output, output_file), "{}/{}".format(
                            report_output, output_file))
            if output_file.endswith('STARtmp'):
                shutil.rmtree("{}/{}".format(align_output, output_file))
                
    def relocate_and_rename_star_output_pe(self):
        """Change the Prefix of STAR output SAM file"""
        os.rename((self.read_alignments_folder + '/' +
                   " ".join(self.get_lib_names_paired_end()) +
                   '_Aligned.out.sam'),
                  (self.read_alignments_folder + '/'
                   + " ".join(str(lib_name) for lib_name in
                              self.get_lib_names_paired_end())
                   + "_alignments_primary_aligner.sam"))
        align_output = self.read_alignments_folder
        for output_file in os.listdir(align_output):
            change_align_output = output_file.replace(
                ".samAligned.out.sam", ".sam")
            if change_align_output != output_file:
                os.rename("{}/{}".format(align_output, output_file),
                          "{}/{}".format(align_output, change_align_output))
            if output_file.endswith("Unmapped.out.mate1"):
                change_unmapped_output_1 = output_file.replace(
                    "Unmapped.out.mate1",
                    "unaligned_1.fa")
                if change_unmapped_output_1 != output_file:
                    os.rename("{}/{}".format(align_output, output_file),
                              "{}/{}".format(self.unaligned_reads_folder,
                                             change_unmapped_output_1))
            if output_file.endswith("Unmapped.out.mate2"):
                change_unmapped_output_2 = output_file.replace(
                    "Unmapped.out.mate2",
                    "unaligned_2.fa")
                if change_unmapped_output_2 != output_file:
                    os.rename("{}/{}".format(align_output, output_file),
                              "{}/{}".format(self.unaligned_reads_folder,
                                             change_unmapped_output_2))

    def gzip_processed_reads(self):
        with gzip.open(output_path, 'rb') as input_fh:
            with gzip.open('{}.gz'.format(output_path), 'wb') as output_fh:
                shutil.copyfileobj(input_fh, output_fh)
        for output_file in os.listdir(self.read_processing_base_folder):
            if output_file.endswith('fa'):
                os.remove('{}/{}'.format(
                    self.read_processing_base_folder, output_file))
