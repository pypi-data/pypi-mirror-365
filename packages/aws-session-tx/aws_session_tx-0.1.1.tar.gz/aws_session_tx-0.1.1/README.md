# AWS Session TX

Track and clean up AWS resources created during development sessions.

## Install

```bash
pip install aws-session-tx
```

## Quick Start

```bash
aws-tx infra deploy
aws-tx begin my-session --ttl 2h
aws s3 mb s3://my-test-bucket
aws-tx status my-session
aws-tx rollback my-session --approve
```

## Commands

| Command | Description |
|---------|-------------|
| `aws-tx begin <name>` | Start session |
| `aws-tx status <name>` | Show status |
| `aws-tx plan <name>` | Show deletion plan |
| `aws-tx rollback <name>` | Delete resources |
| `aws-tx commit <name>` | Keep resources |
| `aws-tx cleanup all` | Clean everything |
| `aws-tx infra deploy` | Deploy infrastructure |
| `aws-tx infra destroy` | Destroy infrastructure |

## Configuration

```bash
export AWS_SESSION_TX_TABLE_NAME=session-tx-dev
```

## Examples

```bash
aws-tx begin dev --ttl 4h
aws-tx rollback dev --approve
```

## License

MIT 