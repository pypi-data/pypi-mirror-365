import pytest
import gen10.advanced as adv
import tempfile
import os
import re

def test_reverse_complement():
    assert adv.reverse_complement("ATGC") == "GCAT"
    assert adv.reverse_complement("AATTCCGG") == "CCGGAATT"
    assert adv.reverse_complement("G") == "C"
    assert adv.reverse_complement("") == ""  # Edge case: empty string

def test_gc_content():
    assert pytest.approx(adv.gc_content("GCGC"), 0.01) == 100.0
    assert pytest.approx(adv.gc_content("ATAT"), 0.01) == 0.0
    assert pytest.approx(adv.gc_content("ATGC"), 0.01) == 50.0
    with pytest.raises(ZeroDivisionError):
        adv.gc_content("")  # Edge case: empty string causes division by zero

def test_melting_temperature():
    assert adv.melting_temperature("ATGC") == 2*(2)+4*(2)  # 2*(A+T) + 4*(G+C)
    assert adv.melting_temperature("AAAA") == 2*4
    assert adv.melting_temperature("GGGG") == 4*4
    assert adv.melting_temperature("ATATAT") == 2*6
    assert adv.melting_temperature("") == 0  # Edge case: empty string

def test_mutate_site():
    # Normal mutation
    assert adv.mutate_site("ATGC", 1, "G") == "AGGC"
    assert adv.mutate_site("ATGC", 0, "T") == "TTGC"
    assert adv.mutate_site("ATGC", 3, "A") == "ATGA"
    
    # Invalid position: negative
    with pytest.raises(ValueError):
        adv.mutate_site("ATGC", -1, "A")
    
    # Invalid position: out of range
    with pytest.raises(ValueError):
        adv.mutate_site("ATGC", 4, "A")
    
    # Invalid new_base
    with pytest.raises(ValueError):
        adv.mutate_site("ATGC", 2, "X")
    
    # Edge case: empty sequence
    with pytest.raises(ValueError):
        adv.mutate_site("", 0, "A")

def test_simulate_pcr_basic():
    sequence = "ATGCGTACGTTAGCTAGCTAGCTAGCGTACGATCG"
    fwd_primer = "ATGCGTACG"
    rev_primer = "CGATCGTAC"
    # The reverse complement of rev_primer is GTACGATCG
    expected_product = sequence[0:sequence.find("GTACGATCG") + len(rev_primer)]
    result = adv.simulate_pcr(sequence, fwd_primer, rev_primer)
    assert result == expected_product

def test_simulate_pcr_primer_not_found():
    sequence = "ATGCGTACGTTAGCTAGCTAGCTAGCGTACGATCG"
    fwd_primer = "AAAAAAA"
    rev_primer = "TTTTTTT"
    result = adv.simulate_pcr(sequence, fwd_primer, rev_primer)
    assert result == ""

def test_simulate_pcr_primers_wrong_order():
    sequence = "ATGCGTACGTTAGCTAGCTAGCTAGCGTACGATCG"
    fwd_primer = "CGATCGTAC"  # This primer is actually reverse primer sequence
    rev_primer = "ATGCGTACG"  # This primer is actually forward primer sequence
    result = adv.simulate_pcr(sequence, fwd_primer, rev_primer)
    assert result == ""

def test_simulate_pcr_partial_match():
    sequence = "ATGCGTACGTTAGCTAGCTAGCTAGCGTACGATCG"
    fwd_primer = "ATGCGTACG"
    rev_primer = "CGATCGTAA"  # last base different, no exact match
    result = adv.simulate_pcr(sequence, fwd_primer, rev_primer)
    assert result == ""

# Tests for get_identifier
def test_get_identifier_dna():
    assert adv.get_identifier("ATCGATCG") == "DNA_sequence" # dna
    assert adv.get_identifier("AUGCAUGC") == "RNA_sequence" # rna
    assert adv.get_identifier("ACDEFGHIKLMNPQRSTVWY") == "Protein_sequence" # protein
    assert adv.get_identifier("XYZ123") == "Unknown_sequence" # wrong characters
    assert adv.get_identifier("ATCGU") == "Unknown_sequence" # mixed bases

# Tests for write_fasta
def test_write_fasta_creates_file_and_content():
    sequence = "ATCG" * 20  # 80 bases
    identifier = "DNA_sequence"
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        filename = tmpfile.name
    try:
        adv.write_fasta(sequence, identifiers=identifier, filename=filename)
        with open(filename, 'r') as f:
            content = f.read()
        # Check header line
        assert content.startswith(f">{identifier}\n")
        # Check sequence lines length (should be 60 bases in first line, 20 in second)
        lines = content.strip().split("\n")
        assert lines[0] == f">{identifier}"
        assert lines[1] == sequence[:60]
        assert lines[2] == sequence[60:]
    finally:
        os.remove(filename)

def test_write_fasta_default_identifier():
    sequence = "AUGC" * 15  # 60 bases, RNA
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        filename = tmpfile.name
    try:
        adv.write_fasta(sequence, filename=filename) # call method without identifier
        
        with open(filename, 'r') as f:
            content = f.readlines()
        
        # The identifier should be RNA
        assert content[0] == f">RNA_sequence\n"
        assert content[1].strip() == sequence[:60]
    finally:
        os.remove(filename)

def test_write_fasta_multiple_sequences():
    sequences = ["AUCGAUCGAU" * 6, "GCTAGCTAGC" * 6]  # 60 bases each
    expected_identifiers = ["RNA_sequence", "DNA_sequence"]  # Expected identifiers

    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        filename = tmpfile.name

    try:
        adv.write_fasta(sequences, identifiers=expected_identifiers, filename=filename)  # Call method with identifiers
        
        with open(filename, 'r') as f:
            content = f.readlines()
        
        # Check the identifiers
        assert content[0] == f">{expected_identifiers[0]}\n"
        assert content[1].strip() == "AUCGAUCGAU"*6
        assert content[2].strip() == ""  # Empty line after first sequence
        assert content[3] == f">{expected_identifiers[1]}\n"
        assert content[4].strip() == "GCTAGCTAGC"*6
        assert content[5].strip() == ""  # Empty line after second sequence

    finally:
        os.remove(filename)

def test_read_fasta_valid():
    # Create a temporary FASTA file with multiple sequences
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
        fasta_content = """>DNA_sequence\nATCGATCGATATCGATCGATATCGATCGATATCGATCG\n>RNA_sequence\nAUCGAUCGAUCGAUCGAUCGAUCGA"""
        temp_file.write(fasta_content.encode('utf-8'))
        temp_file.close()  # Close the file to ensure it's written

        identifiers, sequences = adv.read_fasta(temp_file.name)
        assert identifiers == ["DNA_sequence", "RNA_sequence"]
        assert sequences == [
            "ATCGATCGATATCGATCGATATCGATCGATATCGATCG",
            "AUCGAUCGAUCGAUCGAUCGAUCGA"
        ]

    os.remove(temp_file.name)

def test_read_fasta_empty_file():
    # Create a temporary empty FASTA file
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
        temp_file.close()  # Close the file to ensure it's created

        with pytest.raises(IndexError, match="File is empty"):
            adv.read_fasta(temp_file.name)

    os.remove(temp_file.name)

def test_read_fasta_no_sequence():
    # Create a temporary FASTA file with no sequence
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
        no_sequence_content = """>seq2\n"""  # Only identifier, no sequence
        temp_file.write(no_sequence_content.encode('utf-8'))
        temp_file.close()  # Close the file to ensure it's written

        # Check that reading this file raises a ValueError
        with pytest.raises(ValueError, match=re.escape("FASTA file must contain at least one identifier and one sequence (check that identifiers start with '>')")):
            adv.read_fasta(temp_file.name)

    os.remove(temp_file.name)  # Clean up the temporary file

def test_read_fasta_invalid_format():
    # Create a temporary file with invalid FASTA format
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
        invalid_content = """DNA_sequence\nATCGATCGATCG"""  # Missing '>' in identifier
        temp_file.write(invalid_content.encode('utf-8'))
        temp_file.close()  # Close the file to ensure it's written

        with pytest.raises(ValueError, match=re.escape("FASTA file must contain at least one identifier and one sequence (check that identifiers start with '>')")):
            adv.read_fasta(temp_file.name)

    os.remove(temp_file.name)  # Clean up the temporary file

def test_read_fasta_multiple_sequences():
    # Create a temporary FASTA file with multiple sequences
    with tempfile.NamedTemporaryFile(delete=False, suffix='.fasta') as temp_file:
        fasta_content = """>DNA_sequence\nATCGATCG\n>DNA_sequence\nGCTAGCTA\n>DNA_sequence\nTTAGGCCA"""
        temp_file.write(fasta_content.encode('utf-8'))
        temp_file.close()  # Close the file to ensure it's written

        identifiers, sequences = adv.read_fasta(temp_file.name)
        assert identifiers == ["DNA_sequence", "DNA_sequence", "DNA_sequence"]
        assert sequences == [
            "ATCGATCG",
            "GCTAGCTA",
            "TTAGGCCA"
        ]

    os.remove(temp_file.name)  # Clean up the temporary file

# `genbank_parser` was tested separately and successfully in a notebook