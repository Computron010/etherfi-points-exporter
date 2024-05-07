# Ether.fi Points Exporter

A Prometheus exporter for ether.fi loyalty and EigenLayer points.

## Quickstart

```
docker run -e WALLET=<YOUR WALLET> -p 8000:8000 ghcr.io/computron010/etherfi-points-exporter:main
```

## Docker Environment Variables
| Variable | Description |
| --- | --- |
| `WALLET` | Your wallet address |
| `PORT` | The port to listen on. By default this is `8000`|