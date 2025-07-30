# GbkGen - GenBank File Generator

A comprehensive tool for converting DNA FASTA files to annotated GenBank format with automated gene prediction using Augustus. GbkGen provides a command-line interface for flexible genomic data processing.

## Features

- **FASTA to GenBank Conversion**: Convert DNA sequences from FASTA format to fully annotated GenBank files
- **Automated Gene Prediction**: Integrated Augustus gene prediction with support for multiple species models
- **GFF File Support**: Use existing GFF annotations or generate new ones with Augustus
- **Multiprocessing Support**: Parallel processing for large datasets with configurable CPU cores
- **Multi-sequence Processing**: Handle multiple DNA sequences in a single FASTA file
- **Species-Specific Models**: Configurable Augustus species models for accurate gene prediction
- **Robust Error Handling**: Comprehensive logging and error reporting
- **File Validation**: Automatic validation of input files and compatibility checking
- **Temporary File Management**: Automatic cleanup of intermediate files

## Installation

### Prerequisites
- Python 3.13 or higher
- Augustus gene prediction tool (installed and available in PATH)
- pip or uv package manager

### Using UV (Recommended)
```bash
# Clone the repository
git clone https://github.com/darrengao628/genebank_file_generater
cd genebank_file_generater

# Install with uv
uv sync
```

### Using pip
```bash
# Clone the repository
git clone https://github.com/darrengao628/genebank_file_generater
cd genebank_file_generater

# Install dependencies
pip install -r genebank_file_generater/requirements.txt
```

### Augustus Installation
Make sure Augustus is installed and available in your PATH:

```bash
# For Ubuntu/Debian
sudo apt-get install augustus

# For macOS with Homebrew
brew install augustus

# Or build from source
# Follow instructions at: http://bioinf.uni-greifswald.de/augustus/
```

## Usage

### Command Line Interface

#### Basic Usage

**If installed from source:**
```bash
# Convert FASTA to GenBank (automatically creates input.gbk)
python -m genebank_file_generater.genebank_generater input.fasta

# With custom output filename
python -m genebank_file_generater.genebank_generater input.fasta -o output.gbk

# With specific species model
python -m genebank_file_generater.genebank_generater input.fasta -s human

# Using multiple CPU cores for faster processing
python -m genebank_file_generater.genebank_generater input.fasta -c 8
```

**If installed via pip:**
```bash
# Convert FASTA to GenBank (automatically creates input.gbk)
gbkgen input.fasta

# With custom output filename
gbkgen input.fasta -o output.gbk

# With specific species model
gbkgen input.fasta -s human

# Using multiple CPU cores for faster processing
gbkgen input.fasta -c 8
```

#### Automatic GFF File Detection
The program automatically detects corresponding GFF files:
- If `input.fasta` is provided, it looks for `input.gff` or `input.gff3`
- If found, the GFF file is used automatically (no need for `-g` flag)
- The output filename is always based on the input FASTA filename

```bash
# If 299.fa and 299.gff exist, this automatically uses 299.gff
python -m genebank_file_generater.genebank_generater 299.fa
# Creates 299.gbk as output

# Override automatic GFF detection with explicit GFF file
python -m genebank_file_generater.genebank_generater 299.fa -g custom.gff -o output.gbk
```

#### Advanced Usage
```bash
# Use existing GFF file instead of running Augustus
gbkgen input.fasta -g annotations.gff -o output.gbk

# Specify custom working directory
gbkgen input.fasta -w /tmp/augustus -o output.gbk

# Full example with all options
gbkgen input.fasta \
  --output output.gbk \
  --species aspergillus_fumigatus \
  --workdir ./augustus_output \
  --cpu 4
```

#### Command Line Options
| Option | Short | Description | Default |
|--------|-------|-------------|---------|
| `input` | | Input DNA FASTA file (required) | |
| `--output` | `-o` | Output GenBank file | input.gbk |
| `--species` | `-s` | Augustus species model | aspergillus_fumigatus |
| `--workdir` | `-w` | Working directory for Augustus | ./augustus_output |
| `--gff` | `-g` | Pre-existing GFF3 file | None |
| `--cpu` | `-c` | Number of CPU cores | All available |

## Supported Species Models

GbkGen supports all Augustus species models. Common models include:

- `aspergillus_fumigatus` - Aspergillus fumigatus (default)

For a complete list, run:
```bash
augustus --species=help
```

## Project Structure

```
GbkGen/
├── README.md                           # Main project documentation
├── pyproject.toml                      # Project configuration
├── main.py                             # Simple entry point
├── claude.md                           # Technical analysis
├── genebank_file_generater/            # Core conversion library
│   ├── __init__.py
│   ├── genebank_generater.py          # Main conversion logic
│   ├── gff_parser.py                  # GFF file parsing
│   ├── record.py                      # Record and feature management
│   ├── pyproject.toml                 # Package configuration
│   ├── requirements.txt               # Dependencies
│   ├── README.md                      # Package documentation
│   └── ToDO.md                        # Development roadmap
├── augustus_output/                   # Default Augustus output directory

```

### Getting Help
- Check the [Issues](https://github.com/darrengao628/genebank_file_generater/issues) page
- Review the [ToDO.md](genebank_file_generater/ToDO.md) for known limitations
- Create a new issue with detailed error information


## Changelog

### Version 0.1.0
- Initial release
- Core FASTA to GenBank conversion functionality
- Augustus integration with multiprocessing support
- GFF file parsing and validation
- Comprehensive error handling and logging
- Package distribution support with PyPI
- Simplified dependencies for easier installation


## Acknowledgments

- **BioPython** team for sequence handling libraries
- **Augustus** team for gene prediction software
- **antiSMASH** project for GFF parsing components


---

For more information, visit the [project repository](https://github.com/darrengao628/genebank_file_generater) or contact the development team.