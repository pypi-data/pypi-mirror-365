from typing import TypeVarTuple
from datetime import datetime
from dslog.types import Level

Objs = TypeVarTuple('Objs')

def default(*objs: *Objs, level: Level) -> tuple[str, *Objs]:
  return (f'[{level}] [{datetime.now().strftime("%Y-%m-%d %H:%M:%S")}]', *objs)

def level_color(level: Level):
  match level:
    case 'DEBUG': return 'blue'
    case 'INFO': return 'green'
    case 'WARNING': return 'yellow'
    case 'ERROR': return 'red'
    case 'CRITICAL': return 'bold red'

def click(*objs: *Objs, level: Level) -> tuple[str, *Objs]:
  import click
  col = level_color(level)
  return click.style(f'[{level}]', fg=col), *objs

def rich(*objs: *Objs, level: Level) -> tuple[str, *Objs]:
  col = level_color(level)
  return f'[{col}][{level}][/{col}]', *objs