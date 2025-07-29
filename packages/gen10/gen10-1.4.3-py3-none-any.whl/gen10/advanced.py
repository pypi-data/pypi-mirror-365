import gen10
from Bio import SeqIO
from typing import Dict, List

def reverse_complement(dna):
    """
    This function computes the reverse complement of a given DNA sequence.
    """
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    reverse_comp = ''.join(complement[base] for base in reversed(dna))
    return reverse_comp

def gc_content(dna):
    """
    This function calculates the GC content of a given DNA sequence.
    """
    g_count = dna.count('G')
    c_count = dna.count('C')
    total_count = len(dna)
    gc_content = (g_count + c_count) / total_count * 100
    return gc_content

def melting_temperature(dna):
    """
    Calculates the melting temperature (Tm) of a short DNA sequence using the Wallace rule.
    Assumes DNA is <=14 bases and consists only of A, T, G, and C.
    """
    dna = dna.upper()
    a_count = dna.count('A')
    t_count = dna.count('T')
    g_count = dna.count('G')
    c_count = dna.count('C')

    tm = 2 * (a_count + t_count) + 4 * (g_count + c_count)
    return tm

def mutate_site(sequence, pos, new_base):
    """
    This function mutates a specific site in a DNA or RNA sequence.
    """
    if pos < 0 or pos >= len(sequence):
        raise ValueError("Position out of range")
    if new_base not in ['A', 'T', 'C', 'G', 'U']:
        raise ValueError("Invalid base")
    
    mutated_sequence = list(sequence)
    mutated_sequence[pos] = new_base
    return ''.join(mutated_sequence)


def simulate_pcr(sequence, fwd_primer, rev_primer):
    """
    Simulates a basic PCR reaction on a DNA template.
    """
    # Find the forward primer on the template
    fwd_start = sequence.find(fwd_primer)
    if fwd_start == -1:
        return ""

    # Find the reverse primer's reverse complement on the template
    rev_comp = reverse_complement(rev_primer)
    rev_start = sequence.find(rev_comp)
    if rev_start == -1:
        return ""

    # Make sure primers are in correct orientation and not overlapping
    if fwd_start >= rev_start:
        return ""

    # Calculate the end of the amplified region
    rev_end = rev_start + len(rev_primer)

    return sequence[fwd_start:rev_end]

def get_identifier(sequence):
    """
    Generate a unique identifier for the sequence. Checks whether the sequence is DNA, RNA, or protein.
    """
    if all(base in 'ATCG' for base in sequence):  # DNA check
        return "DNA_sequence"
    elif all(base in 'AUGC' for base in sequence):  # RNA check
        return "RNA_sequence"
    elif all(base in 'ACDEFGHIKLMNPQRSTVWY' for base in sequence):  # Protein check
        return "Protein_sequence"
    else:
        return "Unknown_sequence"

def write_fasta(sequences, identifiers=None, filename="output.fasta"):
    """
    Write multiple sequences to a FASTA file, separated by an empty line.
    
    Parameters:
    sequences (str or list of str): A single sequence as a string or a list of sequences to write.
    identifiers (str or list of str, optional): A single identifier or a list of identifiers corresponding to each sequence. 
                                                 If None, identifiers will be generated using get_identifier.
    filename (str): Name of the output FASTA file.
    """
    # Convert a single sequence string to a list
    if isinstance(sequences, str):
        sequences = [sequences]
    
    # Convert a single identifier string to a list if identifiers are provided
    if identifiers is None:
        identifiers = [get_identifier(seq) for seq in sequences]
    elif isinstance(identifiers, str):
        identifiers = [identifiers]

    with open(filename, 'w') as fasta_file:
        for identifier, sequence in zip(identifiers, sequences):
            fasta_file.write(f">{identifier}\n")
            for i in range(0, len(sequence), 60):
                fasta_file.write(sequence[i:i+60] + "\n")
            fasta_file.write("\n")  # Add an empty line between sequences

def read_fasta(filename):
    """
    Read a FASTA file and return a list of sequences and their corresponding identifiers.
    
    Parameters:
    filename (str): The name of the FASTA file to read.
    
    Returns:
        identifiers (list): A list of identifiers.
        sequences (list): A list of sequences corresponding to the identifiers.
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

        if not lines:  # Check if the list of lines is empty
            raise IndexError("File is empty")
        
        identifiers = []
        sequences = []
        current_sequence = []

        for line in lines:
            line = line.strip()
            if line.startswith(">"):  # New identifier found
                if current_sequence:
                    sequences.append(''.join(current_sequence))
                    current_sequence = []  # Reset for the next sequence
                identifiers.append(line[1:]) # don't save the '>' character
            else:
                current_sequence.append(line)  # Add to the current sequence

        # After the loop, add the last sequence if it exists
        if current_sequence:
            sequences.append(''.join(current_sequence))

        if not identifiers or not sequences:  # Check if we have identifiers and sequences
            raise ValueError("FASTA file must contain at least one identifier and one sequence (check that identifiers start with '>')")

    return identifiers, sequences

def genbank_parser(filepath: str) -> Dict:
    """
    Parse a GenBank file and return a dictionary with relevant information.

    Args:
        filepath (str): The path to the GenBank file.

    Returns:
        Dict: A dictionary containing parsed information from the GenBank file.
    """

    """
    EXAMPLE GenBank FILE:
    LOCUS       1XJI_A                   247 aa            linear   BCT 23-SEP-2004
    DEFINITION  Chain A, Bacteriorhodopsin Crystallized In Bicelles At Room
                Temperature.
    ACCESSION   1XJI_A
    VERSION     1XJI_A  GI:66360541
    DBSOURCE    pdb: molecule 1XJI, chain 65, release Sep 23, 2004;
                deposition: Sep 23, 2004;
                class: Membrane Protein;
                source: Mol_id: 1; Organism_scientific: Halobacterium Salinarium;
                Organism_common: Bacteria; Strain: L33;
                Exp. method: X-Ray Diffraction.
    KEYWORDS    .
    SOURCE      Halobacterium salinarum
    ORGANISM  Halobacterium salinarum
                Archaea; Euryarchaeota; Halobacteria; Halobacteriales;
                Halobacteriaceae; Halobacterium.
    REFERENCE   1  (residues 1 to 247)
    AUTHORS   Faham,S., Boulting,G.L., Massey,E.A., Yohannan,S., Yang,D. and
                Bowie,J.U.
    TITLE     Crystallization of bacteriorhodopsin from bicelle formulations at
                room temperature
    JOURNAL   Protein Sci. 14 (3), 836-840 (2005)
    PUBMED   15689517
    REFERENCE   2  (residues 1 to 247)
    AUTHORS   Faham,S., Boulting,G.L., Massey,E.A., Yohannan,S., Yang,D. and
                Bowie,J.U.
    TITLE     Direct Submission
    JOURNAL   Submitted (23-SEP-2004)
    COMMENT     Revision History:
                APR 19 5 Initial Entry.
    FEATURES             Location/Qualifiers
        source          1..247
                        /organism="Halobacterium salinarum"
                        /db_xref="taxon:2242"
        SecStr          9..32
                        /sec_str_type="helix"
                        /note="helix 1"
        SecStr          36..61
                        /sec_str_type="helix"
                        /note="helix 2"
        SecStr          64..71
                        /sec_str_type="sheet"
                        /note="strand 1"
        SecStr          72..79
                        /sec_str_type="sheet"
                        /note="strand 2"
        SecStr          82..100
                        /sec_str_type="helix"
                        /note="helix 3"
        SecStr          104..126
                        /sec_str_type="helix"
                        /note="helix 4"
        SecStr          130..159
                        /sec_str_type="helix"
                        /note="helix 5"
        SecStr          164..190
                        /sec_str_type="helix"
                        /note="helix 6"
        SecStr          200..224
                        /sec_str_type="helix"
                        /note="helix 7"
        Het             bond(215)
                        /heterogen="(RET, 301 )"
    ORIGIN
            1 aqitgrpewi wlalgtalmg lgtlyflvkg mgvsdpdakk fyaittlvpa iaftmylsml
        61 lgygltmvpf ggeqnpiywa ryadwlfttp lllldlallv dadqgtilal vgadgimigt
        121 glvgaltkvy syrfvwwais taamlyilyv lffgftskae smrpevastf kvlrnvtvvl
        181 wsaypvvwli gsegagivpl nietllfmvl dvsakvgfgl illrsraifg eaeapepsag
        241 dgaaats
    //
    """

    parsed_data = {}

    # Read the GenBank file
    with open(filepath, "r") as file:
        for record in SeqIO.parse(file, "genbank"):
            # Extracting relevant information
            parsed_data['accession'] = record.id
            parsed_data['sequence'] = str(record.seq).lower()  # Convert sequence to lowercase
            parsed_data['organism'] = record.annotations.get('organism', 'Unknown')
            parsed_data['source'] = record.annotations.get('source', 'Unknown')  # Adjusted to capture source
            parsed_data['features'] = []
            parsed_data['references'] = []

            # Extract features
            for feature in record.features:
                feature_info = {
                    'type': feature.type,
                    'location': str(feature.location).replace(":", ".."),  # Adjust location format
                }
                if 'gene' in feature.qualifiers:
                    feature_info['gene'] = feature.qualifiers['gene'][0]
                if 'product' in feature.qualifiers:
                    feature_info['product'] = feature.qualifiers['product'][0]
                parsed_data['features'].append(feature_info)

            # Extract references
            for reference in record.annotations.get('references', []):
                ref_info = {
                    'title': reference.title,
                    'authors': reference.authors if isinstance(reference.authors, list) else [reference.authors],  # Ensure authors are a list
                }
                # Use try/except to handle missing attributes
                try:
                    ref_info['year'] = reference.year
                except AttributeError:
                    ref_info['year'] = 'Unknown'  # Default value if year is not available

                parsed_data['references'].append(ref_info)

    return parsed_data