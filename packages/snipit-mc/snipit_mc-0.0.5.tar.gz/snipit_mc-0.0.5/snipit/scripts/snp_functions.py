#!/usr/bin/env python3

# imports of built-ins
import os
import sys
import argparse
import collections
from itertools import cycle, chain
import csv
import math
from itertools import groupby, count
from collections import OrderedDict
from enum import Enum
import warnings
warnings.filterwarnings('ignore')

# imports from other modules
from Bio import SeqIO
from Bio.Seq import Seq
import matplotlib as mpl
from matplotlib import pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import Polygon, FancyBboxPatch


new_rc_params = {'text.usetex': False,
"svg.fonttype": 'none'
}
mpl.rcParams.update(new_rc_params)


colour_list = ["lightgrey","white"]
colour_cycle = cycle(colour_list)
END_FORMATTING = '\033[0m'
BOLD = '\033[1m'
UNDERLINE = '\033[4m'
RED = '\033[31m'
GREEN = '\033[32m'
YELLOW = '\033[93m'
CYAN = '\u001b[36m'
DIM = '\033[2m'

NT_BASES = ["A","T","G","C"]
NT_AMBIG = ["W","S","M","K","R","Y","B","D","H","V","N"]
AA_BASES = ["A","R","N","D","C","Q","E","G","H","I","L","K","M","F","P","S","T","W","Y","V"]
AA_AMBIG = ["X","B","Z","J"]


def create_rounded_rectangle(xy, width, height, corner_radius=0.1, **kwargs):
    """
    Create a rounded rectangle using FancyBboxPatch.
    
    Args:
        xy: (x, y) tuple for bottom-left corner position
        width: Width of the rectangle
        height: Height of the rectangle  
        corner_radius: Radius for rounded corners (default: 0.1)
        **kwargs: Additional arguments passed to FancyBboxPatch
    
    Returns:
        FancyBboxPatch: Rounded rectangle patch
    """
    # Calculate relative corner radius based on rectangle size
    relative_radius = min(corner_radius, min(width, height) * 0.25)
    
    boxstyle = f"round,pad=0,rounding_size={relative_radius}"
    
    return FancyBboxPatch(
        xy, width, height,
        boxstyle=boxstyle,
        **kwargs
    )


def bp_range(s):
    """
        Crude function to parse positions or position ranges (inclusive) passed as a string by argparse.
        Input: string in the format "100-200" or "100"
        Returns a list with integer positions.
        Arguably better solved by a regex, but still would need to typecast
    """
    # try to parse as a range
    try:
        start,end = map(int, s.split('-'))
        return list(range(start,end+1))
    except ValueError:
        # if range parsing fails, perhaps it's only one position. try to parse as a single int
        try: 
            pos = int(s)
            return [pos]
        except ValueError:
            raise argparse.ArgumentTypeError("Coordinates must be in the format 'start-end' or 'pos'")
        


def check_ref(recombi_mode):
    if recombi_mode:
        sys.stderr.write(red(f"Error: Please explicitly state reference sequence when using `--recombi-mode`\n"))
        sys.exit(-1)

def check_recombi_refs():
    if recombi_mode:
        sys.stderr.write(red(f"Error: Please explicitly state reference sequence when using `--recombi-mode`\n"))
        sys.exit(-1)

def qc_alignment(alignment,reference,cds_mode,sequence_type,cwd):
    lengths = []
    lengths_info = []
    num_seqs = 0

    record_ids = []
    ref_input = ""

    alignment_file = os.path.join(cwd, alignment)
    if not os.path.exists(alignment_file):
        sys.stderr.write(red(f"Error: can't find alignment file at {alignment_file}\n"))
        sys.exit(-1)

    try:
        for record in SeqIO.parse(alignment_file, "fasta"):
            if ref_input == "":
                ref_input = record.id
            lengths.append(len(record))
            record_ids.append(record.id)
            lengths_info.append((record.id, len(record)))
            num_seqs +=1
    except:
        sys.stderr.write(red(f"Error: alignment file must be in fasta format\n"))
        sys.exit(-1)

    if num_seqs == 1:
        if reference:
            if reference.split(".")[-1] not in ["gb","genbank"]:
                sys.stderr.write(red(f"Error: alignment file must contain more than just the reference. Either provide a reference genbank file or add more sequences to your alignment.\n"))
                sys.exit(-1)
        else:
            sys.stderr.write(red(f"Error: alignment file must contain more than just the reference. Either provide a reference genbank file or add more sequences to your alignment.\n"))
            sys.exit(-1)
    unique_lengths = set(lengths)
    if len(unique_lengths)!= 1:
        sys.stderr.write(red("Error: not all of the sequences in the alignment are the same length\n"))
        for i in lengths_info:
            print(f"{i[0]}\t{i[1]}\n")
        sys.exit(-1)
    
    if cds_mode and unique_lengths[0]%3!=0:
        sys.stderr.write(red("Error: CDS mode flag used but alignment length not a multiple of 3.\n"))
        sys.exit(-1)

    print(green(f"Note:") + f" assuming the alignment provided is of type {sequence_type}. If this is not the case, change input --sequence-type")

    return num_seqs,ref_input,record_ids,lengths[0]

def reference_qc(reference, record_ids,cwd):
    ref_file = ""
    if "." in reference and reference.split(".")[-1] in ["gb","genbank"]:
        ref_path = os.path.join(cwd, reference)
        if not os.path.exists(ref_path):
            sys.stderr.write(red(f"Error: can't find genbank file at {ref_path}\n"))
            sys.exit(-1)
        else:
            ref_input = ""
            ref_file = ""
            record_count = 0
            for record in SeqIO.parse(reference, "genbank"):
                ref_input = record.seq
                ref_file = record
                record_count += 1

            if record_count >1:
                sys.stderr.write(red(f"Error: more than one record found in reference genbank file\n"))
                sys.exit(-1)

    elif reference not in record_ids:
        sys.stderr.write(red(f"Error: input reference {reference} not found in alignment\n"))
        sys.exit(-1)

    else:
        ref_input = reference

    return ref_file, ref_input

def recombi_ref_missing():
    sys.stderr.write(red(f"Error: when using --recombi-mode, please supply 2 references separated by a comma with `--recombi-references`.\n"))
    sys.exit(-1)

def recombi_qc(recombi_refs, reference, record_ids,cwd):
    recombi_refs = recombi_refs.split(",")
    if not len(recombi_refs) == 2:
        sys.stderr.write(red(f"Error: input 2 references separated by a comma for `--recombi-references`.\n"))
        sys.exit(-1)

    for ref in recombi_refs:
        if ref == "":
            sys.stderr.write(red(f"Error: input 2 references separated by a comma for `--recombi-references`.\n"))
            sys.exit(-1)
        if ref == reference:
            sys.stderr.write(red(f"Error: please input a distinct outgroup reference from the parent recombinant references specified in `--recombi-references`.\n"))
            sys.exit(-1)
        if ref not in record_ids:
            sys.stderr.write(red(f"Error: please check references specified in `--recombi-references` match a sequence name in the input alignment.\n"))
            sys.exit(-1)



def label_map(record_ids,labels,column_names,cwd):
    seq_col,label_col = column_names.split(",")

    label_map = {}
    if labels:
        label_file = os.path.join(cwd,labels)
        if os.path.exists(label_file):
            with open(label_file, "r") as f:
                reader = csv.DictReader(f)
                if seq_col not in reader.fieldnames:
                    sys.stderr.write(red(f"Error: {seq_col} not a column name in {labels}\n"))
                    sys.exit(-1)
                elif label_col not in reader.fieldnames:
                    sys.stderr.write(red(f"Error: {label_col} not a column name in {labels}\n"))
                    sys.exit(-1)

                for row in reader:
                    sequence_name,label = (row[seq_col],row[label_col])
                    label_map[sequence_name] = label
        else:
            sys.stderr.write(red(f"Error: {record_id} not in {labels} header\n"))
            sys.exit(-1)

        for record_id in record_ids:
            if record_id not in label_map:
                sys.stderr.write(red(f"Error: {record_id} not in {labels} header\n"))
                sys.exit(-1)
    else:
        for record_id in record_ids:
            label_map[record_id] = record_id

    return label_map

def next_colour():
    return next(colour_cycle)

def get_ref_and_alignment(input_file,reference,label_map):
    input_seqs = collections.defaultdict(list)
    reference_seq = ""

    for record in SeqIO.parse(input_file, "fasta"):
        if record.id == reference:
            reference_seq = record.seq.upper()
            if record.id not in label_map:
                label_map["reference"]=record.id
            else:
                label_map["reference"]=label_map[record.id]
        else:
            input_seqs[str(record.seq).upper()].append(record.id)

    return reference_seq, input_seqs

def merge_indels(indel_list,prefix):
    if indel_list:
        groups = groupby(indel_list, key=lambda item, c=count():item-next(c))
        tmp = [list(g) for k, g in groups]
        merged_indels = []
        for i in tmp:
            indel = f"{i[0]}:{prefix}{len(i)}"
            merged_indels.append(indel)
        return merged_indels

    return indel_list

def find_snps(reference_seq,input_seqs,show_indels,sequence_type,ambig_mode):

    # set the appropriate genetic code to use for snp calling
    if sequence_type == 'nt':
        if ambig_mode == 'snps':
            gcode = NT_BASES
        elif ambig_mode == 'all':
            gcode = NT_BASES + NT_AMBIG
        else: # exclude
            gcode = NT_BASES
    if sequence_type == 'aa':
        if ambig_mode == 'snps':
            gcode = AA_BASES
        elif ambig_mode == 'all':
            gcode = AA_BASES + AA_AMBIG
        else: #exclude
            gcode = AA_BASES

    snp_dict = {}

    record_snps = {}
    var_counter = collections.Counter()
    for query_seq in input_seqs:
        snps =[]
        insertions = []
        deletions = []
        for i in range(len(query_seq)):
            bases = [query_seq[i],reference_seq[i]]
            if bases[0] != bases[1]:
                if bases[0] in gcode and bases[1] in gcode:

                    snp = f"{i+1}:{bases[1]}{bases[0]}" # position-reference-query

                    snps.append(snp)
                elif bases[0]=='-' and show_indels:
                #if there's a gap in the query, means a deletion
                    deletions.append(i+1)
                elif bases[1]=='-' and show_indels:
                    #if there's a gap in the ref, means an insertion
                    insertions.append(i+1)
        if show_indels:
            insertions = merge_indels(insertions,"ins")
            deletions = merge_indels(deletions,"del")

        variants = []
        for var_list in [snps,insertions,deletions]:
            for var in var_list:
                var_counter[var]+=1
                variants.append(var)
        variants = sorted(variants, key = lambda x : int(x.split(":")[0]))

        snp_dict[query_seq] = variants

        for record in input_seqs[query_seq]:
            record_snps[record] = variants
    return snp_dict,record_snps,len(var_counter)

def find_ambiguities(alignment, snp_dict,sequence_type):

    if sequence_type == "nt":
        amb = NT_AMBIG
    if sequence_type == "aa":
        amb = AA_AMBIG

    snp_sites = collections.defaultdict(list)
    for seq in snp_dict:
        snps = snp_dict[seq]
        for snp in snps:
            pos,var = snp.split(":")
            index = int(pos)-1

            ref_allele = var[0]
            snp_sites[index]=ref_allele

    amb_dict = {}

    for query_seq in alignment:
        snps =[]

        for i in snp_sites:
            bases = [query_seq[i],snp_sites[i]] #if query not same as ref allele
            if bases[0] != bases[1]:
                if bases[0] in amb:
                    snp = f"{i+1}:{bases[1]}{bases[0]}" # position-outgroup-query
                    snps.append(snp)

        for record in alignment[query_seq]:
            amb_dict[record] = snps

    return amb_dict


def recombi_ref_snps(recombi_references, snp_records):

    recombi_refs = recombi_references.split(",")
    recombi_snps = []
    for ref in recombi_refs:
        recombi_snps.append(snp_records[ref])

    return recombi_snps,recombi_refs

def recombi_painter(snp_to_check,recombi_snps):

    recombi_ref_1 = recombi_snps[0]
    recombi_ref_2 = recombi_snps[1]
    common_snps = []

    for snp in recombi_ref_1:
        if snp in recombi_ref_2:
            common_snps.append(snp)

    if snp_to_check in common_snps:
        return "Both"
    elif snp_to_check in recombi_ref_1:
        return "lineage_1"
    elif snp_to_check in recombi_ref_2:
        return "lineage_2"
    else:
        return "Private"


def write_out_snps(write_snps,record_snps,output_dir):
    with open(os.path.join(output_dir,"snps.csv"),"w") as fw:
        fw.write("record,snps,num_snps\n")
        for record in record_snps:
            snps = ";".join(record_snps[record])
            fw.write(f"{record},{snps},{len(record_snps[record])}\n")


"""
sfunks.make_graph(num_seqs,num_snps,record_ambs,record_snps,
                output,label_map,colours,length,
                args.width,args.height,args.size_option,args.solid_background,
                args.remove_site_text,args.ambig_mode,
                args.flip_vertical,args.included_positions,args.excluded_positions,
                args.sort_by_mutation_number,args.high_to_low, args.sort_by_id,
                      args.sort_by_mutations,
                      args.recombi_mode,
                      args.recombi_references)
"""

def draw_gene_track(ax, features, y_position, y_height, genome_length, colour_palette="classic", sequence_type="nt"):
    """
    Draw a gene track with arrows for genes.
    
    Args:
        ax: matplotlib axis
        features: list of gene features from GenBank
        y_position: y coordinate for gene track
        y_height: height of gene track
        genome_length: total length of the genome
        colour_palette: color palette name to match gene colors
        sequence_type: 'nt' for nucleotide or 'aa' for amino acid
    """
    # Define gene color palettes to match different artistic styles
    # Each palette contains a list of colors that will be assigned to genes in order
    gene_color_schemes = {
        # Classic palette - traditional scientific colors
        "classic": [
            "#2563EB", "#10B981", "#F59E0B", "#EF4444", "#8B5CF6", 
            "#EC4899", "#14B8A6", "#F97316", "#6366F1", "#84CC16",
            "#06B6D4", "#A855F7", "#EAB308", "#3B82F6", "#22C55E"
        ],
        # Nature-style palette - high saturation
        "nature": [
            "#1E40AF", "#059669", "#DC2626", "#7C3AED", "#EA580C", 
            "#0891B2", "#BE123C", "#166534", "#9333EA", "#CA8A04",
            "#0E7490", "#7E22CE", "#B91C1C", "#15803D", "#C2410C"
        ],
        # Morandi palette - muted tones
        "morandi": [
            "#8B7E74", "#7F9173", "#A78F9B", "#9CA3AF", "#B3907A",
            "#94A3B8", "#BFA094", "#A3A78F", "#8F94A3", "#B89B94",
            "#91A3A7", "#A7948F", "#9B8FA3", "#8FA3B8", "#A79B8F"
        ],
        # Van Gogh palette - vibrant contrasts
        "vangogh": [
            "#1E3A8A", "#CA8A04", "#166534", "#7C2D12", "#DC2626",
            "#3730A3", "#0F766E", "#B45309", "#4C1D95", "#991B1B",
            "#1E40AF", "#A16207", "#14532D", "#6B21A8", "#C2410C"
        ],
        # Monet palette - soft impressionist pastels
        "monet": [
            "#93C5FD", "#BBF7D0", "#FECACA", "#E9D5FF", "#FED7AA",
            "#C7D2FE", "#FDE68A", "#BFDBFE", "#D9F99D", "#FBCFE8",
            "#A5F3FC", "#DDD6FE", "#FDE047", "#DBEAFE", "#FCA5A5"
        ],
        # Matisse palette - bold pure colors
        "matisse": [
            "#1D4ED8", "#10B981", "#EF4444", "#F59E0B", "#7C3AED",
            "#EC4899", "#0EA5E9", "#16A34A", "#DC2626", "#EAB308",
            "#9333EA", "#DB2777", "#0284C7", "#22C55E", "#F97316"
        ]
    }
    
    # Get the appropriate color palette
    base_palette = colour_palette.replace("_extended", "").replace("_aa", "")
    if base_palette not in gene_color_schemes:
        base_palette = "classic"
    
    color_list = gene_color_schemes[base_palette]
    
    # Draw background track with rounded corners
    track_bg = create_rounded_rectangle((0, y_position), genome_length, y_height * 2,
                                       corner_radius=0.04, alpha=0.1, fill=True, 
                                       edgecolor='none', facecolor="#E5E7EB", antialiased=True)
    ax.add_patch(track_bg)
    
    # Create a mapping of unique gene names to colors
    unique_genes = []
    gene_color_map = {}
    
    # First pass: collect unique gene names
    for feature in features:
        gene_name = feature["name"]
        if gene_name not in unique_genes:
            unique_genes.append(gene_name)
    
    # Assign colors to each unique gene
    for i, gene_name in enumerate(unique_genes):
        # Cycle through colors if we have more genes than colors
        color_index = i % len(color_list)
        gene_color_map[gene_name] = color_list[color_index]
    
    # Draw genes
    for feature in features:
        start = feature["start"]
        end = feature["end"]
        strand = feature["strand"]
        feat_type = feature["type"]
        name = feature["name"]
        
        # Get color for this specific gene
        color = gene_color_map.get(name, "#6B7280")
        
        # Calculate feature dimensions
        feat_length = end - start
        feat_y = y_position + y_height * 0.2
        feat_height = y_height * 1.6
        
        if strand == 1:  # Forward strand
            # Draw arrow pointing right
            arrow_size = min(feat_length * 0.1, genome_length * 0.01)
            
            # Main rounded rectangle (body of gene)
            rect_width = feat_length - arrow_size
            rect = create_rounded_rectangle((start, feat_y), rect_width, feat_height,
                                          corner_radius=0.1, alpha=0.8, fill=True, 
                                          edgecolor='white', linewidth=1, facecolor=color, antialiased=True)
            ax.add_patch(rect)
            
            # Arrow head
            arrow_points = [
                (start + rect_width, feat_y),
                (end, feat_y + feat_height/2),
                (start + rect_width, feat_y + feat_height)
            ]
            arrow = patches.Polygon(arrow_points, alpha=0.8, fill=True, 
                                  edgecolor='white', linewidth=1,
                                  facecolor=color, antialiased=True)
            ax.add_patch(arrow)
            
        else:  # Reverse strand (-1)
            # Draw arrow pointing left
            arrow_size = min(feat_length * 0.1, genome_length * 0.01)
            
            # Main rounded rectangle (body of gene)
            rect_width = feat_length - arrow_size
            rect = create_rounded_rectangle((start + arrow_size, feat_y), rect_width, feat_height,
                                          corner_radius=0.1, alpha=0.8, fill=True, 
                                          edgecolor='white', linewidth=1, facecolor=color, antialiased=True)
            ax.add_patch(rect)
            
            # Arrow head
            arrow_points = [
                (start + arrow_size, feat_y),
                (start, feat_y + feat_height/2),
                (start + arrow_size, feat_y + feat_height)
            ]
            arrow = patches.Polygon(arrow_points, alpha=0.8, fill=True,
                                  edgecolor='white', linewidth=1,
                                  facecolor=color, antialiased=True)
            ax.add_patch(arrow)
        
        # Add gene name if space permits
        if feat_length > genome_length * 0.02:  # Only show name if gene is large enough
            text_x = start + feat_length/2
            text_y = feat_y + feat_height/2
            
            # Add white background for text
            bbox_props = dict(boxstyle="round,pad=0.2", facecolor='white', 
                            edgecolor='none', alpha=0.8)
            
            ax.text(text_x, text_y, name, size=8, ha="center", va="center",
                   fontweight='medium', bbox=bbox_props)
    
    # Add gene track label
    label = "Gene" if sequence_type == "nt" else "Protein"
    ax.text(-0.01*genome_length, y_position + y_height, label, 
           size=10, ha="right", va="center", fontweight='medium', style='italic')

def make_graph(num_seqs, num_snps, amb_dict, snp_records,
                output, label_map, colour_dict, length,
                width, height, size_option, solid_background,
                remove_site_text,ambig_mode,flip_vertical=False,included_positions=None,excluded_positions=None,
               sort_by_mutation_number=False, high_to_low=True, sort_by_id=False,
               sort_by_mutations=False, recombi_mode=False, recombi_references=[],
               gene_features=None, colour_palette="classic", sequence_type="nt"
               ):
    y_level = 0
    ref_vars = {}
    snp_dict = collections.defaultdict(list)
    included_positions = set(chain.from_iterable(included_positions)) if included_positions is not None else set()
    excluded_positions = set(chain.from_iterable(excluded_positions)) if excluded_positions is not None else set()

    if sort_by_mutation_number:
        snp_counts = {}
        for record in snp_records:
            snp_counts[record] = int(len(snp_records[record]))
        ordered_dict = dict(sorted(snp_counts.items(), key=lambda item: item[1], reverse=high_to_low))
        record_order = list(OrderedDict(ordered_dict).keys())

    elif sort_by_id:
        record_order = list(sorted(snp_records.keys()))

    elif sort_by_mutations:
        mutations = sort_by_mutations.split(",")
        sortable_record = {}
        for record in snp_records:
            bases = []
            for sort_mutation in mutations:
                found = False
                for record_mutation in snp_records[record]:
                    if int(record_mutation.split(":")[0]) == int(sort_mutation):
                        bases.append(record_mutation[-1])
                        found = True
                        break
                if not found:
                    bases.append("0")
            sortable_record[record] = "".join(bases) + record
        record_order = list(OrderedDict(sorted(sortable_record.items(), key=lambda item: item[1], reverse=high_to_low)).keys())

    else:
        record_order = list(snp_records.keys())
    if recombi_mode:
        # Get a list of SNPs present in each recombi_reference
        recombi_snps,recombi_refs = recombi_ref_snps(recombi_references, snp_records)
        # Set the colour palette to "recombi"
        colour_dict = get_colours("recombi")
        # Reorder list to put recombi_references at the start
        record_order.remove(recombi_refs[0])
        record_order.insert(0, recombi_refs[0])
        record_order.remove(recombi_refs[1])
        record_order.insert(1, recombi_refs[1])

    for record in record_order:
        # y level increments per record, add a gap after the two recombi_refs
        if recombi_mode and y_level == 2:
            y_level += 1.2
        else:
            y_level +=1

        # for each record get the list of snps
        snps = snp_records[record]
        x = []
        y = []

        for snp in snps:
            # snp => 12345AT
            pos,var = snp.split(":")
            x_position = int(pos)
            if var.startswith("del"):
                length_indel = var[3:]
                ref = f"{length_indel}"
                base = "-"
            elif var.startswith("ins"):
                length_indel = var[3:]
                ref = "-"
                base = f"{length_indel}"
            else:
                ref = var[0]
                base = var[1]

            ref_vars[x_position]=ref
            if recombi_mode:
                recombi_out = recombi_painter(snp, recombi_snps)
                # Add name of record, ref, SNP in record, y_level, if SNP is in either recombi_reference...
                snp_dict[x_position].append((record, ref, base, y_level, recombi_out))
            else:
                # ...otherwise add False instead to help the colour logic
                snp_dict[x_position].append((record, ref, base, y_level, False))

        # if there are ambiguities in that record, add them to the snp dict too
        if record in amb_dict:
            for amb in sorted(amb_dict[record]):
                # amb => 12345AN
                pos,var = amb.split(":")
                x_position = int(pos)

                # if positions with any ambiguities should be ignored, note the position
                if ambig_mode == 'exclude':
                    excluded_positions.add(x_position)
                else:
                    ref = var[0]
                    base = var[1]
                    ref_vars[x_position]=ref
                    # Add name of record, ref, SNP in record, y_level and False for "recombi_mode" colour logic
                    snp_dict[x_position].append((record, ref, base, y_level, False))


    # gather the positions that are not explicitly excluded,
    # but are not among those to be included
    positions_not_included=set()
    if len(included_positions)>0:
        # of the positions present,
        # gather a set of positions which should NOT be included in the output
        positions_not_included = set(snp_dict.keys()) - included_positions

    # remove positions which should be ignored or are not included (pop items from union of the two sets)
    for pos in excluded_positions | positions_not_included:
        # remove records for the position, if present
        snp_dict.pop(pos, None)

    spacing = length/(len(snp_dict)+1)
    y_inc = (spacing*0.8*y_level)/length

    if size_option == "expand":
        if not width:
            if num_snps ==0:
                print(red(f"Note: no SNPs found between the reference and the alignment"))
                width = 10
            else:
                if len(snp_dict) <10:
                    width = 10
                else:
                    width = 0.25* len(snp_dict)

        if not height:
            if y_level < 5:
                height = 5
            else:
                height = (y_inc*3 + 0.5*y_level + y_inc*2) # bottom chunk, and num seqs, and text on top

    elif size_option == "scale":
        if not width:
            if num_snps == 0:
                print(red(f"Note: no SNPs found between the reference and the alignment"))
                width = 12
            else:
                width = math.sqrt(num_snps)*3

        if not height:
            height = math.sqrt(num_seqs)*2
            y_inc = 1

    # if the plot is flipped vertically, place the x-axis (genome map) labels on top
    if flip_vertical:
        plt.rcParams['xtick.bottom'] = plt.rcParams['xtick.labelbottom'] = False
        plt.rcParams['xtick.top'] = plt.rcParams['xtick.labeltop'] = True

    # Set matplotlib parameters for better quality
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['DejaVu Sans', 'Helvetica', 'Arial', 'sans-serif']
    plt.rcParams['font.size'] = 11
    plt.rcParams['axes.linewidth'] = 1.5
    plt.rcParams['xtick.major.width'] = 1.5
    plt.rcParams['ytick.major.width'] = 1.5
    plt.rcParams['xtick.major.size'] = 4
    plt.rcParams['ytick.major.size'] = 4
    
    # width and height of the figure with higher DPI for better quality
    fig, ax = plt.subplots(1,1, figsize=(width,height), dpi=300, facecolor='white')

    y_level = 0

    for record in record_order:

        # y position increments, with a gap after the two recombi_refs
        if recombi_mode and y_level == 2:
            y_level += y_inc + 0.2
        else:
            y_level += y_inc


        # either grey or white
        col = next_colour()

        # for each record (sequence) draw a rounded rectangle the length of the whole genome (either grey or white)
        rect = create_rounded_rectangle((0,y_level-(0.5*y_inc)), length, y_inc,
                                       corner_radius=0.05, alpha=0.25, fill=True, 
                                       edgecolor='none', facecolor=col, antialiased=True)
        ax.add_patch(rect)

        # for each record add the name to the left hand side with background
        # Add subtle background box for label
        bbox_props = dict(boxstyle="round,pad=0.3", facecolor='#F3F4F6', edgecolor='none', alpha=0.7)
        ax.text(-0.01*length, y_level, label_map[record], size=11, ha="right", va="center", fontweight='medium', bbox=bbox_props)

    position = 0
    for snp in sorted(snp_dict):
        position += spacing

        # write text adjacent to the SNPs shown with the numeric position
        # the text alignment is toggled right/left (top/bottom considering 90-deg rotation) if the plot is flipped
        if not remove_site_text:
            # Add background for position number
            bbox_props = dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='#E5E7EB', linewidth=0.5, alpha=0.9)
            ax.text(position, y_level+(0.55*y_inc), snp, size=9, ha="center", va="bottom" if not flip_vertical else "top", rotation=90, fontweight='medium', color='#374151', bbox=bbox_props)

        # snp position labels
        left_of_box = position-(0.4*spacing)
        right_of_box = position+(0.4*spacing)

        top_polygon = y_inc * -0.7
        bottom_polygon = y_inc * -1.7

        for sequence in snp_dict[snp]:

            name,ref,var,y_pos,recombi_out = sequence
            bottom_of_box = (y_pos*y_inc)-(0.5*y_inc)
            # draw rounded box for snp
            if recombi_out:
                rect = create_rounded_rectangle((left_of_box,bottom_of_box),spacing*0.85,  y_inc*0.9,
                                              corner_radius=0.15, alpha=0.8, fill=True, 
                                              edgecolor='white',linewidth=0.5,facecolor=colour_dict[recombi_out], antialiased=True)
            elif var in colour_dict:
                rect = create_rounded_rectangle((left_of_box,bottom_of_box),spacing*0.85,  y_inc*0.9,
                                              corner_radius=0.15, alpha=0.8, fill=True, 
                                              edgecolor='white',linewidth=0.5,facecolor=colour_dict[var.upper()], antialiased=True)
            else:
                rect = create_rounded_rectangle((left_of_box,bottom_of_box), spacing*0.85,  y_inc*0.9,
                                              corner_radius=0.15, alpha=0.8, fill=True, 
                                              edgecolor='white',linewidth=0.5,facecolor="dimgrey", antialiased=True)

            ax.add_patch(rect)

            # sequence variant text with shadow
            if not remove_site_text:
                # Add shadow
                ax.text(position+0.02*spacing, (y_pos*y_inc)-0.02*y_inc, var, size=10, ha="center", va="center", fontweight='bold', color='black', alpha=0.3)
                # Main text
                ax.text(position, y_pos*y_inc, var, size=10, ha="center", va="center", fontweight='bold', color='white')

        # reference variant text with shadow
        if not remove_site_text:
            # Add shadow
            ax.text(position+0.02*spacing, (y_inc * -0.2)-0.02*y_inc, ref, size=10, ha="center", va="center", fontweight='medium', color='black', alpha=0.2)
            # Main text
            ax.text(position, y_inc * -0.2, ref, size=10, ha="center", va="center", fontweight='medium')

        #polygon showing mapping from genome to spaced out snps
        x = [snp-0.5,snp+0.5,right_of_box,left_of_box,snp-0.5]
        y = [bottom_polygon,bottom_polygon,top_polygon,top_polygon,bottom_polygon]
        coords = list(zip(x, y))

        # draw polygon with gradient effect
        poly = patches.Polygon(coords, alpha=0.08, fill=True, edgecolor='#CCCCCC',linewidth=0.5,facecolor="#4A5568", antialiased=True)
        ax.add_patch(poly)

        rect = create_rounded_rectangle((left_of_box,top_polygon), spacing*0.85, y_inc*0.95,
                                       corner_radius=0.12, alpha=0.12, fill=True, 
                                       edgecolor='#E0E0E0',linewidth=0.5,facecolor="#718096", antialiased=True)
        ax.add_patch(rect)

    if len(snp_dict) == 0:
        # snp position labels
        left_of_box = position-(0.4*position)
        right_of_box = position+(0.4*position)

        top_polygon = y_inc * -0.7
        bottom_polygon = y_inc * -1.7


    # reference variant rounded rectangle with enhanced style
    rect = create_rounded_rectangle((0,(top_polygon)), length, y_inc,
                                   corner_radius=0.08, alpha=0.2, fill=True, 
                                   edgecolor='#CBD5E0',linewidth=1,facecolor="#64748B", antialiased=True)
    ax.add_patch(rect)

    # Add reference label with enhanced style
    bbox_props = dict(boxstyle="round,pad=0.3", facecolor='#1F2937', edgecolor='none', alpha=0.9)
    ax.text(-0.01*length,  y_inc * -0.2, label_map["reference"], size=12, ha="right", va="center", fontweight='bold', style='italic', color='white', bbox=bbox_props)

    ref_genome_position = y_inc*-2.7

    # reference genome rounded rectangle with gradient-like effect
    # Bottom darker layer
    rect_bottom = create_rounded_rectangle((0,ref_genome_position), length, y_inc*0.5,
                                          corner_radius=0.06, alpha=0.25, fill=True, 
                                          edgecolor='none',facecolor="#374151", antialiased=True)
    ax.add_patch(rect_bottom)
    # Top lighter layer
    rect_top = create_rounded_rectangle((0,ref_genome_position+y_inc*0.5), length, y_inc*0.5,
                                       corner_radius=0.06, alpha=0.15, fill=True, 
                                       edgecolor='none',facecolor="#6B7280", antialiased=True)
    ax.add_patch(rect_top)
    # Border
    rect_border = create_rounded_rectangle((0,ref_genome_position), length, y_inc,
                                          corner_radius=0.06, alpha=1, fill=False, 
                                          edgecolor='#9CA3AF',linewidth=1, antialiased=True)
    ax.add_patch(rect_border)

    for var in ref_vars:
        ax.plot([var,var],[ref_genome_position+y_inc*0.02,ref_genome_position+(y_inc*0.98)], color="#DC2626", linewidth=2, alpha=0.7, antialiased=True, solid_capstyle='round')

    # Draw gene track if features are provided
    if gene_features:
        gene_track_position = ref_genome_position - y_inc * 2
        draw_gene_track(ax, gene_features, gene_track_position, y_inc, length, colour_palette, sequence_type)

    # Remove all plot borders/spines
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_visible(False)
    ax.spines['bottom'].set_visible(False)

    plt.yticks([])

    # Add extra space on the left for labels
    ax.set_xlim(-0.05*length,length)
    
    # Adjust y-axis limits to accommodate gene track if present
    bottom_limit = ref_genome_position
    if gene_features:
        bottom_limit = ref_genome_position - y_inc * 3  # Extra space for gene track
    
    if not flip_vertical:
        ax.set_ylim(bottom_limit,y_level+(y_inc*1.05))
    else:
        ax.set_ylim(bottom_limit,y_level+(y_inc*2.05))
        ax.invert_yaxis() # must be called after axis limits are set

    ax.tick_params(axis='x', labelsize=9)
    plt.xlabel("Position (base)", fontsize=12, fontweight='medium')
    # Adjust layout with more padding
    plt.tight_layout(pad=1.5)
    
    # Save with high quality settings
    if not solid_background:
        plt.savefig(output, transparent=True, bbox_inches='tight', pad_inches=0.2, edgecolor='none')
    else:
        plt.savefig(output, bbox_inches='tight', pad_inches=0.2, facecolor='white', edgecolor='none')

def get_colours(colour_palette):

    palettes = {"classic": {"A":"steelblue","C":"indianred","T":"darkseagreen","G":"skyblue"},
                "classic_extended": {"A":"steelblue","C":"indianred","T":"darkseagreen",
                                     "G":"skyblue","W":"#FFCC00","S":"#66FF00","M":"#6600FF",
                                     "K":"#66FFCC","R":"#FF00FF","Y":"#FFFF99","B":"#CCFF99",
                                     "D":"#FFFF00","H":"##33FF00","V":"#FF6699","N":"#333333"},
                "nature": {"A":"#3572AF","C":"#E94B3C","T":"#F39C12","G":"#00A08A"},
                "nature_extended": {"A":"#3572AF","C":"#E94B3C","T":"#F39C12","G":"#00A08A",
                                    "W":"#FFC300","S":"#6FA8DC","M":"#8E44AD","K":"#1ABC9C",
                                    "R":"#E74C3C","Y":"#F1C40F","B":"#3498DB","D":"#2ECC71",
                                    "H":"#9B59B6","V":"#16A085","N":"#2C3E50"},
                "morandi": {"A":"#A8A5A0","C":"#C4ADA0","T":"#B5B3A7","G":"#9A9B94"},
                "morandi_extended": {"A":"#A8A5A0","C":"#C4ADA0","T":"#B5B3A7","G":"#9A9B94",
                                    "W":"#D4C5B9","S":"#A7B0B3","M":"#B8A8A3","K":"#9FA5A3",
                                    "R":"#BFB5B2","Y":"#C9C2B2","B":"#B0B5B8","D":"#AFAFA5",
                                    "H":"#C0B5B0","V":"#A0A8A5","N":"#8B8680"},
                "vangogh": {"A":"#1E3A8A","C":"#F59E0B","T":"#FDE047","G":"#10B981"},
                "vangogh_extended": {"A":"#1E3A8A","C":"#F59E0B","T":"#FDE047","G":"#10B981",
                                    "W":"#FBBF24","S":"#3B82F6","M":"#7C3AED","K":"#059669",
                                    "R":"#DC2626","Y":"#FCD34D","B":"#2563EB","D":"#16A34A",
                                    "H":"#9333EA","V":"#0D9488","N":"#1F2937"},
                "monet": {"A":"#93C5FD","C":"#F9A8D4","T":"#BBF7D0","G":"#DDD6FE"},
                "monet_extended": {"A":"#93C5FD","C":"#F9A8D4","T":"#BBF7D0","G":"#DDD6FE",
                                  "W":"#FEF3C7","S":"#BFDBFE","M":"#E9D5FF","K":"#A7F3D0",
                                  "R":"#FBCFE8","Y":"#FDE68A","B":"#DBEAFE","D":"#D1FAE5",
                                  "H":"#EDE9FE","V":"#CCFBF1","N":"#E5E7EB"},
                "matisse": {"A":"#EF4444","C":"#3B82F6","T":"#10B981","G":"#F59E0B"},
                "matisse_extended": {"A":"#EF4444","C":"#3B82F6","T":"#10B981","G":"#F59E0B",
                                    "W":"#F97316","S":"#6366F1","M":"#EC4899","K":"#14B8A6",
                                    "R":"#DC2626","Y":"#FCD34D","B":"#2563EB","D":"#059669",
                                    "H":"#DB2777","V":"#0891B2","N":"#6B7280"},
                "wes": {"A":"#CC8B3C","C":"#456355","T":"#541F12","G":"#B62A3D"},
                "primary": {"A":"green","C":"goldenrod","T":"steelblue","G":"indianred"},
                "purine-pyrimidine":{"A":"indianred","C":"teal","T":"teal","G":"indianred"},
                "greyscale":{"A":"#CCCCCC","C":"#999999","T":"#666666","G":"#333333"},
                "blues":{"A":"#3DB19D","C":"#76C5BF","T":"#423761","G":"steelblue"},
                "verity":{"A":"#EC799A","C":"#df6eb7","T":"#FF0080","G":"#9F0251"},
                "recombi":{"lineage_1":"steelblue","lineage_2":"#EA5463","Both":"darkseagreen","Private":"goldenrod"},
                "ugene":{"A":"#00ccff","R":"#d5c700","N":"#33ff00","D":"#ffff00","C":"#6600ff","Q":"#3399ff",
                         "E":"#c0bdbb","G":"#ff5082","H":"#fff233","I":"#00abed","L":"#008fc6","K":"#ffee00",
                         "M":"#1dc0ff","F":"#3df490","P":"#d5426c","S":"#ff83a7","T":"#ffd0dd","W":"#33cc78",
                         "Y":"#65ffab","V":"#ff6699","X":"#999999","B":"#999999","Z":"#999999","J":"#999999"},
                "nature_aa":{"A":"#3572AF","R":"#E94B3C","N":"#F39C12","D":"#00A08A","C":"#8B5CF6","Q":"#06B6D4",
                            "E":"#059669","G":"#EA580C","H":"#7C3AED","I":"#0891B2","L":"#2563EB","K":"#DC2626",
                            "M":"#7C2D12","F":"#84CC16","P":"#EC4899","S":"#F59E0B","T":"#10B981","W":"#4F46E5",
                            "Y":"#BE123C","V":"#0EA5E9","X":"#6B7280","B":"#6B7280","Z":"#6B7280","J":"#6B7280"},
                "morandi_aa":{"A":"#A8A5A0","R":"#C4ADA0","N":"#B5B3A7","D":"#9A9B94","C":"#B8A8A3","Q":"#A7B0B3",
                             "E":"#9FA5A3","G":"#BFB5B2","H":"#C0B5B0","I":"#A0A8A5","L":"#B0B5B8","K":"#C9C2B2",
                             "M":"#AFAFA5","F":"#D4C5B9","P":"#B5ABA5","S":"#C5BCB0","T":"#ABA8A0","W":"#A5A09B",
                             "Y":"#BCB5A8","V":"#A8A8A0","X":"#8B8680","B":"#8B8680","Z":"#8B8680","J":"#8B8680"},
                "vangogh_aa":{"A":"#1E3A8A","R":"#F59E0B","N":"#FDE047","D":"#10B981","C":"#7C3AED","Q":"#3B82F6",
                             "E":"#059669","G":"#DC2626","H":"#9333EA","I":"#0891B2","L":"#2563EB","K":"#EF4444",
                             "M":"#92400E","F":"#65A30D","P":"#DB2777","S":"#F97316","T":"#14B8A6","W":"#6366F1",
                             "Y":"#BE123C","V":"#0EA5E9","X":"#374151","B":"#374151","Z":"#374151","J":"#374151"},
                "monet_aa":{"A":"#93C5FD","R":"#F9A8D4","N":"#BBF7D0","D":"#DDD6FE","C":"#E9D5FF","Q":"#BFDBFE",
                           "E":"#D1FAE5","G":"#FBCFE8","H":"#EDE9FE","I":"#CCFBF1","L":"#DBEAFE","K":"#FDE68A",
                           "M":"#D5F4E6","F":"#FEF3C7","P":"#FCE7F3","S":"#FED7AA","T":"#A7F3D0","W":"#C7D2FE",
                           "Y":"#FECDD3","V":"#CFFAFE","X":"#E5E7EB","B":"#E5E7EB","Z":"#E5E7EB","J":"#E5E7EB"},
                "matisse_aa":{"A":"#EF4444","R":"#3B82F6","N":"#10B981","D":"#F59E0B","C":"#EC4899","Q":"#6366F1",
                             "E":"#059669","G":"#DC2626","H":"#DB2777","I":"#0891B2","L":"#2563EB","K":"#F97316",
                             "M":"#78350F","F":"#84CC16","P":"#BE185D","S":"#FB923C","T":"#14B8A6","W":"#7C3AED",
                             "Y":"#991B1B","V":"#0284C7","X":"#6B7280","B":"#6B7280","Z":"#6B7280","J":"#6B7280"}
                }
    if colour_palette not in palettes:
        sys.stderr.write(red(f"Error: please select one of {palettes} for --colour-palette option\n"))
        sys.exit(-1)
    else:
        colour_dict = palettes[colour_palette]

    return colour_dict

def check_size_option(s):
    size_options = ["expand", "scale"]
    s_string = "\n - ".join(size_options)
    if s not in size_options:
        sys.stderr.write(red(f"Error: size option specified not one of:\n - {s_string}\n"))
        sys.exit(-1)

def check_format(f):
    formats = ["png", "jpg", "pdf", "svg", "tiff"]
    f_string = "\n - ".join(formats)
    if f not in formats:
        sys.stderr.write(red(f"Error: format specified not one of:\n - {f_string}\n"))
        sys.exit(-1)

def colour(text, text_colour):
    bold_text = 'bold' in text_colour
    text_colour = text_colour.replace('bold', '')
    underline_text = 'underline' in text_colour
    text_colour = text_colour.replace('underline', '')
    text_colour = text_colour.replace('_', '')
    text_colour = text_colour.replace(' ', '')
    text_colour = text_colour.lower()
    if 'red' in text_colour:
        coloured_text = RED
    elif 'green' in text_colour:
        coloured_text = GREEN
    elif 'yellow' in text_colour:
        coloured_text = YELLOW
    elif 'dim' in text_colour:
        coloured_text = DIM
    elif 'cyan' in text_colour:
        coloured_text = 'cyan'
    else:
        coloured_text = ''
    if bold_text:
        coloured_text += BOLD
    if underline_text:
        coloured_text += UNDERLINE
    if not coloured_text:
        return text
    coloured_text += text + END_FORMATTING
    return coloured_text

def red(text):
    return RED + text + END_FORMATTING

def cyan(text):
    return CYAN + text + END_FORMATTING

def green(text):
    return GREEN + text + END_FORMATTING

def yellow(text):
    return YELLOW + text + END_FORMATTING

def parse_genbank(genbank_file, cwd):
    """
    Parse a GenBank file and extract gene features for visualization.
    
    Args:
        genbank_file: Path to GenBank file
        cwd: Current working directory
    
    Returns:
        List of gene features with positions, names, and types
    """
    import os
    from Bio import SeqIO
    
    gb_path = os.path.join(cwd, genbank_file)
    
    if not os.path.exists(gb_path):
        sys.stderr.write(red(f"Error: GenBank file {genbank_file} not found\n"))
        return None
    
    features = []
    
    try:
        # Parse GenBank file
        for record in SeqIO.parse(gb_path, "genbank"):
            for feature in record.features:
                if feature.type in ["gene", "CDS", "rRNA", "tRNA", "ncRNA", "regulatory"]:
                    # Extract feature information
                    start = int(feature.location.start)
                    end = int(feature.location.end)
                    strand = feature.location.strand  # 1 for forward, -1 for reverse
                    
                    # Get feature name
                    name = None
                    if "gene" in feature.qualifiers:
                        name = feature.qualifiers["gene"][0]
                    elif "locus_tag" in feature.qualifiers:
                        name = feature.qualifiers["locus_tag"][0]
                    elif "product" in feature.qualifiers:
                        name = feature.qualifiers["product"][0][:20]  # Truncate long product names
                    else:
                        name = feature.type
                    
                    features.append({
                        "start": start,
                        "end": end,
                        "strand": strand,
                        "type": feature.type,
                        "name": name
                    })
            
            # Only process the first record (reference sequence)
            break
                
    except Exception as e:
        sys.stderr.write(red(f"Error parsing GenBank file: {str(e)}\n"))
        return None
    
    # Sort features by start position
    features.sort(key=lambda x: x["start"])
    
    return features
