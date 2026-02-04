# SPI Scripts - ReversingLabs Spectra Intelligence CLI

Command-line tool for querying all [ReversingLabs Spectra Intelligence](https://www.reversinglabs.com/products/spectra-intelligence) APIs. Supports 20 API endpoints covering file reputation, malware hunting, network threat intelligence, and more.

## Setup

### 1. Install dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure credentials

Edit `config.ini` with your ReversingLabs username and password:

```ini
[reversinglabs]
host = https://data.reversinglabs.com
username = your_actual_username
password = your_actual_password
```

## Usage

```bash
python spi.py <command> [options]
```

Use `--debug` for verbose request/response logging:

```bash
python spi.py --debug <command> [options]
```

### Output

All results are saved as JSON files in the `output/` directory. The file path is printed to stdout after each query. Use `-o <path>` to override the output location.

## Available Commands

### File Threat Intelligence

| Command | API | Description |
|---|---|---|
| `reputation` | TCA-0101 | File reputation (MALICIOUS, SUSPICIOUS, KNOWN, UNKNOWN) |
| `av-scanners` | TCA-0103 | Historic multi-AV scan records (40+ scanners) |
| `file-analysis` | TCA-0104 | Full file analysis (static analysis, AV scans, certificates) |
| `dynamic-report` | TCA-0106 | Dynamic analysis report from ReversingLabs Cloud Sandbox |

### Automation

| Command | API | Description |
|---|---|---|
| `download` | TCA-0201 | Download a sample binary |
| `upload` | TCA-0202 | Upload a file for analysis |
| `reanalyze` | TCA-0205 | Trigger re-analysis of a file |
| `dynamic-analysis` | TCA-0207 | Submit file/URL for sandbox detonation |

### Malware Hunting

| Command | API | Description |
|---|---|---|
| `rha-similarity` | TCA-0301 | RHA functional similarity search |
| `imphash` | TCA-0302 | ImpHash similarity search |
| `search` | TCA-0320 | Advanced search with 110+ keywords |

### Network Threat Intelligence

| Command | API | Description |
|---|---|---|
| `uri-index` | TCA-0401 | Find files associated with a URI |
| `uri-stats` | TCA-0402 | Classification statistics for a URI |
| `url-report` | TCA-0403 | URL threat intelligence report |
| `analyze-url` | TCA-0404 | Submit URL for analysis |
| `domain-report` | TCA-0405 | Domain threat intelligence report |
| `ip-report` | TCA-0406 | IP address threat intelligence report |
| `net-reputation` | TCA-0407 | Network reputation for URL/domain/IP |
| `net-override` | TCA-0408 | Override network reputation classification |

### Management

| Command | API | Description |
|---|---|---|
| `usage` | TCA-9999 | View daily/monthly API usage |

## Examples

### Single hash lookup

```bash
python spi.py reputation --hash 275a021bbfb6489e54d471899f7db9d1663fc695ec2fe2a2c4538aabf651fd0f
python spi.py reputation --hash <sha256> --extended --show-hashes
```

### Bulk queries (comma-separated)

```bash
python spi.py reputation --hash <hash1>,<hash2>,<hash3>
```

### Bulk queries (from file)

```bash
# hashes.txt: one hash per line
python spi.py reputation --hash-file hashes.txt
```

### Network threat intelligence

```bash
python spi.py url-report --url "http://example.com"
python spi.py domain-report --domain "example.com"
python spi.py ip-report --ip "1.2.3.4"
python spi.py net-reputation --network-location "http://example.com"
python spi.py net-override --location "http://example.com" --type url --classification malicious
```

### Advanced search

```bash
python spi.py search --query "av-count:5 type:PE32"
python spi.py search --query "threatname:Trojan.GenericKD" --limit 50
```

### File operations

```bash
python spi.py upload --file sample.exe
python spi.py download --hash <sha1> -o downloaded_sample.bin
python spi.py reanalyze --hash <sha256>
python spi.py dynamic-analysis --hash <sha1> --platform windows10
```

### Sandbox reports

```bash
python spi.py dynamic-report --hash <sha1>
python spi.py dynamic-report --hash <sha1> --latest
```

### Custom output path

```bash
python spi.py reputation --hash <sha256> -o results/my_report.json
```

## Project Structure

```
spi.py                  # Entry point
config.ini              # Credentials (not tracked by git)
requirements.txt        # Python dependencies
spi_cli/
├── main.py             # CLI argument parsing and command routing
├── config.py           # Configuration file loader
├── client.py           # HTTP client with auth and logging
├── output.py           # JSON output file handler
├── hash_utils.py       # Hash parsing and type detection
├── xml_utils.py        # XML response parsing (some APIs return XML)
└── commands/           # One module per API endpoint (20 modules)
```

## Adding a New Command

1. Create a new file in `spi_cli/commands/` (e.g. `my_command.py`)
2. Implement `register(subparsers)` and `execute(args, client)` functions
3. Import and add the module to `COMMAND_MODULES` and `COMMAND_MAP` in `spi_cli/main.py`

## Authentication

All requests use HTTP Basic Authentication (`Authorization: Basic base64(username:password)`) against `https://data.reversinglabs.com`. Credentials are read from `config.ini` at runtime.

## API Reference

Full API documentation: https://docs.reversinglabs.com/SpectraIntelligence/

OpenAPI specification: https://docs.reversinglabs.com/openapi-bundled.yaml
