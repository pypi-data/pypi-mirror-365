import logging
import os
from datetime import datetime

from . import anchor, composite, contour, guideline, metric, misc
from .base import GlyphCommand

log = logging.getLogger(__name__)

glyphCommandRegistry = {}


def registerGlyphCommand(command, group):
    assert issubclass(command, GlyphCommand)
    assert isinstance(group, str)
    if group not in glyphCommandRegistry:
        glyphCommandRegistry[group] = {}
    glyphCommandRegistry[group][command.name] = command


def getCommandClass(name):
    for group in glyphCommandRegistry:
        if name in glyphCommandRegistry[group]:
            return glyphCommandRegistry[group][name]
    return None


def getCommandFromString(string):
    name, paramStr = [s.strip() for s in string.strip().split(":", 1)]
    commandClass = getCommandClass(name)
    if commandClass and issubclass(commandClass, GlyphCommand):
        return commandClass.fromString(paramStr)
    return None


def loadCommandList(filename):
    commandList = []
    if os.path.isfile(filename):
        with open(filename, "r", encoding="utf-8") as commandListFile:
            for line in commandListFile:
                line = line.strip()
                if line and not line.startswith("#"):
                    if "#" in line:
                        line = line.split("#", 1)[0]
                    try:
                        command = getCommandFromString(line)
                    except:
                        log.error('Can not read command: "%s"', line)
                        command = None
                    if isinstance(command, GlyphCommand):
                        commandList.append(command)
    return commandList


def saveCommandList(commandList, filename):
    folder = os.path.dirname(filename)
    if not os.path.isdir(folder):
        os.makedirs(folder)
    with open(filename, "w", encoding="utf-8") as commandListFile:
        commandListFile.write("# UFO WorkBench Command List\n")
        commandListFile.write(f'# saved: {datetime.now().isoformat(" ")}\n\n')
        for command in commandList:
            if isinstance(command, GlyphCommand):
                commandListFile.write(str(command) + "\n")


def executeCommandList(commandList, glyphs):
    fonts = set()
    for glyph in glyphs:
        glyph.holdNotifications()
        for command in commandList:
            command.execute(glyph)
        glyph.destroyRepresentation("outlineErrors")
        glyph.postNotification("Glyph.Changed")
        glyph.releaseHeldNotifications()
        fonts.add(glyph.font)
    for font in fonts:
        font.document.UpdateAllViews(sender=None, hint=None)


# register all available commands
for module in (contour, composite, metric, anchor, guideline, misc):
    group = module.__name__.rsplit(".", 1)[-1].title()
    for name in dir(module):
        obj = getattr(module, name)
        if (
            obj is not GlyphCommand
            and isinstance(obj, type)
            and issubclass(obj, GlyphCommand)
        ):
            registerGlyphCommand(obj, group)
