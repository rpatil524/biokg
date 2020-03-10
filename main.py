# -*- coding: utf-8 -*-

from os.path import join, isdir, exists
from os import mkdir
from configparser import RawConfigParser

from biokg.loader import *
from biokg.util.extras import program_header
from biokg.processing.parsers import *
from biokg.util.io import export_file_md5, file_has_valid_md5


def main():
    """ Program entry point
    """
    print_bold_line()
    print(program_header)
    print_bold_line()

    # define work directories and files
    data_dp = "./data/"
    sources_dp = join(data_dp, "sources")
    preprocessed_dp = join(data_dp, "preprocessed")
    output_dp = join(data_dp, "output")
    sources_fp = "./sources.ini"

    # create directories if not existing
    mkdir(data_dp) if not isdir(data_dp) else None
    mkdir(sources_dp) if not isdir(sources_dp) else None
    mkdir(preprocessed_dp) if not isdir(preprocessed_dp) else None
    mkdir(output_dp) if not isdir(output_dp) else None
    
    # load sources' urls
    sources_urls = RawConfigParser()
    sources_urls.read(sources_fp)

    # download uniprot source data

    download_uniprot_files(sources_dp=sources_dp, srcs_cp=sources_urls)

    # download reactome source data

    download_reactome_data(sources_dp=sources_dp, srcs_cp=sources_urls)

    # download cellosaurus source data
    download_cellosaurus_data(sources_dp=sources_dp, srcs_cp=sources_urls)

    # download hpa source data
    download_hpa_data(sources_dp=sources_dp, srcs_cp=sources_urls)

    # download ctd source data
    download_ctd_data(sources_dp=sources_dp, srcs_cp=sources_urls)
    
    # download phosphosite source data
    download_phosphosite_data(sources_dp=sources_dp, srcs_cp=sources_urls)

    # download intact source data
    download_intact_data(sources_dp=sources_dp, srcs_cp=sources_urls)

    # download sider source data
    download_sider_data(sources_dp=sources_dp, srcs_cp=sources_urls)
    # ----------------------------------------------------------------------
    # processing uniprot entries file
    uniprot_parser = UniProtTxtParser()
    uniprot_entries_fp = join(sources_dp, "swissprot_human_entries.txt.gz")
    uniprot_output_files = ["uniprot_facts.txt", "uniprot_metadata.txt", "uniprot_ppi.txt"]
    uniprot_output_fps = [join(output_dp, fn) for fn in uniprot_output_files]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in uniprot_output_fps]))

    if invalid_md5:
        uniprot_parser.parse(uniprot_entries_fp, output_dp)
        for ofp in uniprot_output_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "Uniprot processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

    # ----------------------------------------------------------------------
    # processing HPA entries file
    hpa_parser = HumanProteinAtlasParser()
    hpa_files = ["hpa_antibodies.txt", "hpa_cellines_exp.txt", "hpa_tissues_exp.txt"]
    hpa_fps = [join(preprocessed_dp, fn) for fn in hpa_files]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in hpa_fps]))
    if invalid_md5:
        hpa_parser.parse_database_xml(join(sources_dp, "proteinatlas.xml.gz"), preprocessed_dp)
        for ofp in hpa_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "HPA processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)
    # ----------------------------------------------------------------------
    # processing Cellosaurus database file
    cell_parser = CellosaurusParser()
    cell_parser.parse_db_file(join(sources_dp, "cellosaurus_data.txt"), preprocessed_dp)

    # TODO: export md5 hashes of resulting files as in other databases

    # ----------------------------------------------------------------------
    # processing DrugBank entries file
    drugbank_source_fp = join(sources_dp, "drugbank_all_full_database.xml.zip")
    drugbank_parser = DrugBankParser()
    drugbank_fps = [join(preprocessed_dp, fn) for fn in drugbank_parser.filelist]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in drugbank_fps]))
    if invalid_md5:
        # Skip drugbank processing if the file is not in the source folder
        if exists(drugbank_source_fp):
            drugbank_parser.parse_drugbank_xml(drugbank_source_fp, preprocessed_dp)
            for ofp in drugbank_fps:
                export_file_md5(ofp)
        else:
            print(fail_sym + "Drugbank source not available >>> Skipping Drugbank processing")
    else:
        print(inf_sym + "DrugBank processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

    # ----------------------------------------------------------------------
    # processing KEGG links
    kegg_parser = KeggParser()
    kegg_fp = join(preprocessed_dp, kegg_parser.filename)
    invalid_md5 = not file_has_valid_md5(kegg_fp)
    if invalid_md5:
        kegg_parser.parse_kegg(preprocessed_dp)
        export_file_md5(kegg_fp)
    else:
        print(inf_sym + "KEGG processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

    # ----------------------------------------------------------------------
    # processing Reactome entries file
    reactome_parser = ReactomeParser()
    reactome_fps = [join(preprocessed_dp, fn) for fn in reactome_parser.filenames]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in reactome_fps]))

    if invalid_md5:
        reactome_parser.parse_reactome(sources_dp, preprocessed_dp)
        for ofp in reactome_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "Reactome processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

    # ----------------------------------------------------------------------
    # processing CTD entries file
    ctd_parser = CTDParser()
    ctd_fps = [join(preprocessed_dp, fn) for fn in ctd_parser.filenames]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in ctd_fps]))

    if invalid_md5:
        ctd_parser.parse_ctd(sources_dp, preprocessed_dp)
        for ofp in ctd_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "CTD processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)
    
    # ----------------------------------------------------------------------
    # processing Phosphosite entries file
    phosphosite_parser = PhosphositeParser()
    phosphosite_fps = [join(preprocessed_dp, fn) for fn in phosphosite_parser.filenames]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in phosphosite_fps]))

    if invalid_md5:
        phosphosite_parser.parse_phosphosite(sources_dp, preprocessed_dp)
        for ofp in phosphosite_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "PhosphoSitePlus processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

    # ----------------------------------------------------------------------
    # processing Intact zip file
    intact_parser = IntactParser()
    intact_fps = [join(preprocessed_dp, fn) for fn in intact_parser.filenames]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in intact_fps]))

    if invalid_md5:
        intact_parser.parse_intact(sources_dp, preprocessed_dp, join(output_dp, 'uniprot_ppi.txt'))
        for ofp in intact_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "Intact processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

    # ----------------------------------------------------------------------
    # processing Sider files
    sider_parser = SiderParser()
    sider_fps = [join(preprocessed_dp, fn) for fn in sider_parser.filenames]
    invalid_md5 = bool(sum([not file_has_valid_md5(ofp) for ofp in sider_fps]))

    if invalid_md5:
        sider_parser.parse_sider(sources_dp, preprocessed_dp)
        for ofp in sider_fps:
            export_file_md5(ofp)
    else:
        print(inf_sym + "Sider processed files exists with valid md5 hashes %s. >>> Parsing not required." % done_sym)

if __name__ == '__main__':
    main()
