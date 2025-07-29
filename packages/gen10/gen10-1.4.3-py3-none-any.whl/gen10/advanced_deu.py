import gen10
from Bio import SeqIO
from typing import Dict, List

def komplementare(dna):
    """
    Diese Funktion berechnet das komplementäre Gegenstück (Reverse Complement) einer gegebenen DNA-Sequenz.
    """
    complement = {'A': 'T', 'T': 'A', 'C': 'G', 'G': 'C'}
    reverse_comp = ''.join(complement[base] for base in reversed(dna))
    return reverse_comp

def gc_gehalt(dna):
    """
    Diese Funktion berechnet den GC-Gehalt einer gegebenen DNA-Sequenz.
    """
    g_count = dna.count('G')
    c_count = dna.count('C')
    total_count = len(dna)
    gc_content = (g_count + c_count) / total_count * 100
    return gc_content

def schmelz_temperatur(dna):
    """
    Berechnet die Schmelztemperatur (Tm) einer kurzen DNA-Sequenz unter Verwendung der Wallace-Regel.
    Geht davon aus, dass die DNA <=14 Basen hat und nur aus A, T, G und C besteht.
    """
    dna = dna.upper()
    a_count = dna.count('A')
    t_count = dna.count('T')
    g_count = dna.count('G')
    c_count = dna.count('C')

    tm = 2 * (a_count + t_count) + 4 * (g_count + c_count)
    return tm

def stelle_mutieren(sequence, pos, new_base):
    """
    Diese Funktion mutiert eine spezifische Stelle in einer DNA- oder RNA-Sequenz.
    """
    if pos < 0 or pos >= len(sequence):
        raise ValueError("Stelle außerhalb des Bereichs")
    if new_base not in ['A', 'T', 'C', 'G', 'U']:
        raise ValueError("Ungültige Base")
    
    mutated_sequence = list(sequence)
    mutated_sequence[pos] = new_base
    return ''.join(mutated_sequence)

def pcr_simulieren(sequence, fwd_primer, rev_primer):
    """
    Simulates a basic PCR reaction on a DNA template.
    """
    # Find the forward primer on the template
    fwd_start = sequence.find(fwd_primer)
    if fwd_start == -1:
        return ""

    # Find the reverse primer's reverse complement on the template
    rev_comp = komplementare(rev_primer)
    rev_start = sequence.find(rev_comp)
    if rev_start == -1:
        return ""

    # Make sure primers are in correct orientation and not overlapping
    if fwd_start >= rev_start:
        return ""

    # Calculate the end of the amplified region
    rev_end = rev_start + len(rev_primer)

    return sequence[fwd_start:rev_end]

def typ_bestimmen(sequence):
    """
    Eine Funktion, die den Typ der Sequenz bestimmt (DNA, RNA oder Protein).
    """
    if all(base in 'ATCG' for base in sequence):  # DNA check
        return "DNA_sequence"
    elif all(base in 'AUGC' for base in sequence):  # RNA check
        return "RNA_sequence"
    elif all(base in 'ACDEFGHIKLMNPQRSTVWY' for base in sequence):  # Protein check
        return "Protein_sequence"
    else:
        return "Unknown_sequence"

def fasta_schreiben(sequences, identifiers=None, filename="output.fasta"):
    """
    Schreibt eine Liste von Sequenzen in eine FASTA-Datei.
    Parameters:
        sequences (list): Liste von Sequenzen
        identifiers (list): Liste von Identifikatoren (optional)
        filename (str): Name der Ausgabedatei (optional, Standard: "output.fasta")
    """
    # Convert a single sequence string to a list
    if isinstance(sequences, str):
        sequences = [sequences]
    
    # Convert a single identifier string to a list if identifiers are provided
    if identifiers is None:
        identifiers = [typ_bestimmen(seq) for seq in sequences]
    elif isinstance(identifiers, str):
        identifiers = [identifiers]

    with open(filename, 'w') as fasta_file:
        for identifier, sequence in zip(identifiers, sequences):
            fasta_file.write(f">{identifier}\n")
            for i in range(0, len(sequence), 60):
                fasta_file.write(sequence[i:i+60] + "\n")
            fasta_file.write("\n")  # Add an empty line between sequences

def fasta_lesen(filename):
    """
    Liest eine FASTA-Datei und gibt die Sequenzen und ihre Identifikatoren zurück.
    Parameters:
        filename (str): Name der FASTA-Datei
    Returns:
        identifiers (list): Liste von Identifikatoren
        sequences (list): Liste von Sequenzen
    """
    with open(filename, 'r') as f:
        lines = f.readlines()

        if not lines:  # Check if the list of lines is empty
            raise IndexError("Leere Datei")
        
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
            raise ValueError("Fehler beim Lesen der Datei: Keine Identifikatoren oder Sequenzen gefunden (Typ muss mit '>' anfangen)")

    return identifiers, sequences

def genbank_lesen(filepath):
    """
    Liest eine GenBank-Datei und gibt die Information zurück.
    Parameters:
        filepath (str): Der Pfad zur GenBank-Datei
    Returns:
        parsed_data (dict): Ein Dictionary mit den Informationen aus der GenBank-Datei
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