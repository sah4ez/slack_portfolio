## pyenv

For local development install [pyenv](https://github.com/pyenv/pyenv-installer)

Create virtual env:
```bash
pyenv viratul 3.8.8 portfolio
pyenv activate portfolio
```

And install requirements:
```bash
pip install -r ./requirements.txt
```

Or build docker:
```
make build
```

## System environment

Local run:
```
env TOKEN_BOT=<TELEGRAM_TOKEN_BOT> python main.py
```

or Docker:
```
make run TOKEN_BOT=<TELEGRAM_TOKEN_BOT>
```
