import keyboard
from colorama import Fore, Back, Style
import os
import re
import sys


def count(string: str, findStr: str) -> int:
    return len(re.findall(findStr, string))


def delete_last_lines(n=1):
    """
    Deletes the last n printed lines in the terminal
    """
    CURSOR_UP_ONE = "\x1b[1A"
    ERASE_LINE = "\x1b[2K"
    for _ in range(n):
        sys.stdout.write(CURSOR_UP_ONE)
        sys.stdout.write(ERASE_LINE)


def removeColorama(text: str) -> str:
    # Remove Fore
    text = (
        text.replace(Fore.BLACK, "")
        .replace(Fore.RED, "")
        .replace(Fore.GREEN, "")
        .replace(Fore.YELLOW, "")
        .replace(Fore.BLUE, "")
        .replace(Fore.MAGENTA, "")
        .replace(Fore.CYAN, "")
        .replace(Fore.WHITE, "")
        .replace(Fore.RESET, "")
    )
    # Remove Back
    text = (
        text.replace(Back.BLACK, "")
        .replace(Back.RED, "")
        .replace(Back.GREEN, "")
        .replace(Back.YELLOW, "")
        .replace(Back.BLUE, "")
        .replace(Back.MAGENTA, "")
        .replace(Back.CYAN, "")
        .replace(Back.WHITE, "")
        .replace(Back.RESET, "")
    )
    # Remove Style
    text = (
        text.replace(Style.BRIGHT, "")
        .replace(Style.DIM, "")
        .replace(Style.NORMAL, "")
        .replace(Style.RESET_ALL, "")
    )
    # Remove Parentheses due to re module conflicts under os.get_terminal_size()
    text = text.replace("(", " ").replace(")", " ")
    return text


def nLines(n: int = 1):
    """
    Prints n new lines in the terminal
    """
    for _ in range(n):
        print("")


def getNumLinesFromTerminal(toPrint: str):
    """
    Returns the number of lines that would be printed in the terminal
    """
    termWidth = os.get_terminal_size().columns
    return ((len(toPrint) - 1) // termWidth) + count("\n", toPrint)


def splitRangeFromNum(num: str, selectRange: str) -> str:
    start, end = tuple([int(i) for i in selectRange.split("-")])
    num = int(num)
    curString = ""
    numTrack1 = 0
    numTrack2 = 0
    # 11-22
    # Num = 13
    # 12-22
    for indice in range(start, end + 1):
        if indice != num and numTrack1 == 0:
            numTrack1 = indice
        if indice == num and numTrack1 == 0:
            continue
        if indice + 1 == num and numTrack1 > 0 and indice == numTrack1:
            curString += f"{numTrack1},"
            numTrack1 = 0
        elif indice + 1 == num and numTrack1 > 0 and indice != numTrack1:
            numTrack2 = indice
            curString += f"{numTrack1}-{numTrack2},"
            numTrack1 = 0
            numTrack2 = 0
        elif indice == end:
            numTrack2 = indice
            curString += f"{numTrack1}-{numTrack2},"
            numTrack1 = 0
            numTrack2 = 0
    return curString[:-1]


def removeNumFromInput(num: str, inputBar: str) -> str:
    currentNum = ""
    nums = []
    parsedOut = []
    if "," in inputBar:
        for entry in inputBar.split(","):
            if "-" in entry:
                addDash = True
                for entry2 in entry.split("-"):
                    if entry2 != "":
                        nums.append(entry2)
                    if addDash == True:
                        nums.append("-")
                        addDash = False
            else:
                if entry != num:
                    nums.append(entry)
    elif "-" in inputBar:
        addDash = True
        for entry2 in inputBar.split("-"):
            if entry2 != "":
                nums.append(entry2)
            if addDash == True:
                nums.append("-")
                addDash = False
    else:
        if inputBar != num:
            nums.append(inputBar)
    # print(nums)
    for indice in range(len(nums)):
        if indice + 1 != len(nums):
            if nums[indice + 1] == "-":
                continue
            elif nums[indice - 1] == "-" and indice != 0:
                continue
            elif nums[indice] == "-":
                parsedOut.append(
                    splitRangeFromNum(num, f"{nums[indice-1]}-{nums[indice+1]}")
                )
            elif (
                nums[indice - 1] != "-"
                and nums[indice + 1] != "-"
                and nums[indice] != num
            ):
                parsedOut.append(f"{nums[indice]}")
            elif indice == 0 and nums[indice + 1] != "-" and nums[indice] != num:
                parsedOut.append(f"{nums[indice]}")
        elif indice + 1 == len(nums):
            # print(f"Indice + 1 {indice+1}, len(nums) {len(nums)}")
            if nums[indice - 1] == "-":
                continue
            elif nums[indice - 1] != "-" and nums[indice] != num:
                parsedOut.append(f"{nums[indice]}")
    return ",".join([entry for entry in parsedOut if entry != "-" and entry != ""])


def massSelectionInput_Parser(inputBar: str, listLen: int) -> tuple:
    """
    Selection Types
    {
        selection: (indexStart <int>, indexEnd <int>),
        type: range
    }
    {
        selection: (index <int>),
        type: single
    }
    """
    if len(inputBar) == 0:
        return inputBar, []
    selectionTypes = []
    "12-15,17,19-21"
    "12-15"
    "12,17"
    "12"
    "12,"
    "-12"
    # Irregular Syntax for Input
    if ",-" in inputBar:
        inputBar = inputBar.replace(",-", ",")
    if "-," in inputBar:
        inputBar = inputBar.replace("-,", ",")
    if "--" in inputBar:
        inputBar = inputBar.replace("--", "-")
    if ",," in inputBar:
        inputBar = inputBar.replace(",,", ",")
    if ("-" == inputBar[0] or "," == inputBar[0]) and len(inputBar) > 1:
        inputBar = inputBar[1:]
    # Parse Input
    passStatus = False
    if "," in inputBar:
        for value in inputBar.split(","):
            passStatus = False
            if len(value) == 0:
                continue
            if "-" in value:
                selectionType = "range"
                try:
                    startIndex, endIndex = tuple(value.split("-"))
                except ValueError:
                    startIndex, endIndex = tuple(value[:-1].split("-"))
                # If condition: 17-
                if len(endIndex) == 0:
                    if int(startIndex) > listLen:
                        inputBar = listLen
                    selectionType = "single"
                    selectionTypes.append(
                        {"selection": startIndex, "type": selectionType}
                    )
                    passStatus = True
                    continue
                # If condition: 9999-99999 or 1-99999 or 99999-1
                if (
                    int(startIndex) > listLen
                    or int(endIndex) > listLen
                    or int(startIndex) == int(endIndex)
                    or int(startIndex) > int(endIndex)
                ):
                    # If condition: 99999-5
                    if int(startIndex) > listLen:
                        startIndex = listLen
                    # If condition: 5-99999
                    if int(endIndex) > listLen:
                        endIndex = listLen
                    # If condition: 0
                    if int(startIndex) == 0:
                        startIndex = 1
                    if int(endIndex) == 0:
                        endIndex = 1
                    # If condition: 123-10
                    # if int(startIndex) > int(endIndex):
                    #     startIndex, endIndex = endIndex, startIndex
                    # Update inputBar
                    if startIndex != endIndex:
                        inputBar = inputBar.replace(value, f"{startIndex}-{endIndex}")
                    # If condition: 123-
                    if startIndex == endIndex:
                        # inputBar = inputBar.replace(value, f"{startIndex}")
                        selectionType = "single"
                        selectionTypes.append(
                            {"selection": int(startIndex), "type": selectionType}
                        )
                        passStatus = True
                if passStatus == False:
                    selectionTypes.append(
                        {
                            "selection": (int(startIndex), int(endIndex)),
                            "type": selectionType,
                        }
                    )
            else:
                # Single value
                index = int(value)
                if int(index) > listLen:
                    index = listLen
                    inputBar = inputBar.replace(value, str(index))
                if int(index) == 0:
                    index = 1
                    inputBar = inputBar.replace(value, str(index))
                selectionType = "single"
                selectionTypes.append({"selection": index, "type": selectionType})
    elif "-" in inputBar:
        # If condition: 1-
        selectionType = "range"
        try:
            startIndex, endIndex = tuple(inputBar.split("-"))
        except ValueError:
            startIndex, endIndex = tuple(inputBar[:-1].split("-"))
        # If condition: 17-
        if len(endIndex) == 0:
            if int(startIndex) > listLen:
                startIndex = listLen
            selectionType = "single"
            selectionTypes.append({"selection": startIndex, "type": selectionType})
            passStatus = True
        # If condition: 9999-99999 or 1-99999 or 99999-1
        elif (
            int(startIndex) > listLen
            or int(endIndex) > listLen
            or int(startIndex) == int(endIndex)
            or int(startIndex) > int(endIndex)
        ):
            # If condition: 99999-5
            if int(startIndex) > listLen:
                startIndex = listLen
            # If condition: 5-99999
            if int(endIndex) > listLen:
                endIndex = listLen
            # If condition: 0
            if int(startIndex) == 0:
                startIndex = 1
            if int(endIndex) == 0:
                endIndex = 1
            # If condition: 123-10
            # if int(startIndex) > int(endIndex):
            #     startIndex, endIndex = endIndex, startIndex
            # Update inputBar
            if startIndex != endIndex:
                inputBar = inputBar.replace(inputBar, f"{startIndex}-{endIndex}")
            # If condition: 123-
            if startIndex == endIndex:
                # inputBar = inputBar.replace(inputBar, f"{startIndex}")
                selectionType = "single"
                selectionTypes.append(
                    {"selection": int(startIndex), "type": selectionType}
                )
                passStatus = True
        if passStatus == False:
            selectionTypes.append(
                {"selection": (int(startIndex), int(endIndex)), "type": selectionType}
            )
    else:
        if int(inputBar) > listLen:
            inputBar = listLen
        if int(inputBar) == 0:
            inputBar = 1
        selectionTypes.append({"selection": int(inputBar), "type": "single"})
    selectionIndices = []
    [
        (
            selectionIndices.append(int(entry["selection"]))
            if entry["type"] == "single"
            else (
                [
                    selectionIndices.append(indice)
                    for indice in range(
                        entry["selection"][0], entry["selection"][1] + 1
                    )
                ]
                if entry["type"] == "range"
                else ()
            )
        )
        for entry in selectionTypes
    ]
    return str(inputBar), sorted(list(set(selectionIndices)))


def curIndexCalc(
    curIndex: int, startIndex: int, endIndex: int, limit: int, listLen: int
) -> tuple:
    # listLen -= 1
    if curIndex == -1:
        curIndex = listLen - 1
        startIndex = listLen - limit
        endIndex = listLen
    elif curIndex < startIndex:
        startIndex -= 1
        endIndex -= 1
    if curIndex == listLen:
        curIndex = 0
        startIndex = 0
        endIndex = limit
    elif curIndex >= endIndex:
        startIndex += 1
        endIndex += 1
    # 53, 67, 68
    # 54, 53, 69
    if startIndex < curIndex and endIndex < curIndex:
        if (listLen - limit) < curIndex:
            startIndex = listLen - limit
            endIndex = listLen
        elif (listLen - limit) > curIndex:
            startIndex = curIndex
            endIndex = curIndex + limit
    elif startIndex > curIndex and endIndex > curIndex:
        if curIndex < limit:
            startIndex = 0
            endIndex = limit
        elif curIndex > limit:
            startIndex = curIndex
            endIndex = curIndex + limit
    return curIndex, startIndex, endIndex


class get:
    def selectionInput(
        header: str,
        selectionList: list,
        limit: int = 15,
        debug: bool = False,
        entrySymbol: tuple = ("○", "●"),
    ) -> int:
        """
        Custom Selection Input
        Use arrows up and down to navigate through the list
        """
        select1, select2 = entrySymbol
        if limit > len(selectionList):
            limit = len(selectionList)
        curIndex = 0
        startIndex = 0
        endIndex = limit
        print(header)
        while True:
            delLineAmount = limit
            for i in range(startIndex, endIndex):
                curLine = f"{selectionList[i]}"
                curPrint = ""
                if "\n" in curLine:
                    curLine = curLine.replace("\n", f"{Style.RESET_ALL}\n   \t»  ")
                if i != curIndex:
                    curPrint = f"{select1}  {i+1})\t{curLine.replace(Fore.YELLOW, '')}"
                else:
                    # Selected Entry
                    curPrint = f"{Fore.YELLOW}{Style.BRIGHT}{select2}  {i+1})\t{curLine}{Style.RESET_ALL}"
                print(curPrint)
                delLineAmount += getNumLinesFromTerminal(removeColorama(curPrint))
            if debug == True:
                delLineAmount += 1
                print(
                    f"""Start: {startIndex}, Current: {curIndex}, End: {endIndex}, Delete Lines: {delLineAmount}"""
                )
            key = keyboard.read_key()
            if keyboard.is_pressed("up") or keyboard.is_pressed("w"):
                curIndex -= 1
                # Total = 25
                # Start: 0, Current: -1, End: 15
                if curIndex == -1:
                    curIndex = len(selectionList) - 1
                    startIndex = len(selectionList) - limit
                    endIndex = len(selectionList)
                elif curIndex < startIndex:
                    startIndex -= 1
                    endIndex -= 1
            if keyboard.is_pressed("down") or keyboard.is_pressed("s"):
                curIndex += 1
                # Total = 25
                # Start: 14, Current: 25, End: 25
                if curIndex == len(selectionList):
                    curIndex = 0
                    startIndex = 0
                    endIndex = limit
                elif curIndex >= endIndex:
                    startIndex += 1
                    endIndex += 1
            if key == "enter":
                return curIndex
            delete_last_lines(delLineAmount)

    def massSelectionInput(
        header: str,
        selectionList: list,
        limit: int = 15,
        debug: bool = False,
        entrySymbol: tuple = ("○", "●", "✔"),
    ) -> list:
        """
        Input dict:
        selectionList = {
            1: {
                title: str,
                ...
            },
            ...
        }
        """
        nums = "1234567890-,"
        selIndices = []
        inputBar = ""
        helpCond = False
        inputIndex, goToIndex, findIndex = 0, 0, 0
        select1, select2, checked = entrySymbol
        if limit > len(selectionList):
            limit = len(selectionList)
        curIndex, startIndex = 0, 0
        endIndex = limit
        termSize = os.get_terminal_size()
        print(header)
        while True:
            delLineAmount = limit
            curPrint = ""
            if helpCond == False:
                for i in range(startIndex, endIndex):
                    title = selectionList[i]["title"]
                    if "\n" in title:
                        title = title.replace("\n", f"{Style.RESET_ALL}\n   \t»  ")
                    if (i != curIndex) and (i + 1 not in selIndices):
                        curPrint = f"{select1}  {i+1})\t{title}"
                    elif (i != curIndex) and (i + 1 in selIndices):
                        curPrint = f"{checked}  {i+1})\t{Back.WHITE}{Fore.BLACK}{title}{Style.RESET_ALL}"
                    elif (i == curIndex) and (i + 1 in selIndices):
                        curPrint = f"{Fore.YELLOW}{Style.BRIGHT}{select2}  {i+1})\t{Back.WHITE}{title}{Style.RESET_ALL}"
                    else:
                        # Selected Entry
                        curPrint = f"{Fore.YELLOW}{Style.BRIGHT}{select2}  {i+1})\t{title}{Style.RESET_ALL}"
                    print(curPrint)
                    delLineAmount += getNumLinesFromTerminal(removeColorama(curPrint))
                curPrint = f"{Style.BRIGHT}{inputBar[:inputIndex]}{Fore.BLUE}┃{Style.RESET_ALL}{inputBar[inputIndex:]}{Style.RESET_ALL}"
                delLineAmount += getNumLinesFromTerminal(removeColorama(curPrint))
                print(curPrint)
            if helpCond == True:
                delLineAmount = 0
                selChapterFuncs = [
                    f"[{Style.BRIGHT}{Fore.BLUE}a{Style.RESET_ALL}] to select all entries",
                    f"[{Style.BRIGHT}{Fore.BLUE}Space{Style.RESET_ALL}] to select/unselect specific entry",
                    f"[{Style.BRIGHT}{Fore.BLUE}g{Style.RESET_ALL}] to go to a specific entry",
                    "Press any key to go back to the selection list",
                ]
                for a in selChapterFuncs:
                    print(a)
                    delLineAmount += getNumLinesFromTerminal(removeColorama(a)) + 1
                delLineAmount -= 1
            if debug == True:
                delLineAmount += 1
                print(
                    f"""Start: {startIndex}, Current: {curIndex}, End: {endIndex}, Delete Lines: {delLineAmount}, findIndex: {findIndex}, Limit: {limit}, numLine: {getNumLinesFromTerminal(f'{inputBar[:inputIndex]}┃{inputBar[inputIndex:]}')}, term: {termSize.columns}"""
                )
            key = get.getKey()
            # Keys for List Selection
            if key == "up" or key == "w":
                curIndex -= 1
                # Total = 25
                # Start: 0, Current: -1, End: 15
                curIndex, startIndex, endIndex = curIndexCalc(
                    curIndex=curIndex,
                    startIndex=startIndex,
                    endIndex=endIndex,
                    limit=limit,
                    listLen=len(selectionList),
                )
            elif key == "down" or key == "s":
                curIndex += 1
            # Keys for input bar
            else:
                if key == "left":
                    inputIndex -= 1
                    if inputIndex == -1:
                        inputIndex = len(inputBar)
                elif key == "right":
                    inputIndex += 1
                    if inputIndex == len(inputBar) + 1:
                        inputIndex = 0
                elif key == "a":
                    if f"1-{len(selectionList)}" in inputBar:
                        inputBar = (
                            inputBar.replace(f",1-{len(selectionList)},", "")
                            .replace(f",1-{len(selectionList)}", "")
                            .replace(f"1-{len(selectionList)},", "")
                            .replace(f"1-{len(selectionList)}", "")
                        )
                        inputIndex = len(inputBar)
                    else:
                        inputBar += f",1-{len(selectionList)}"
                        inputIndex = len(inputBar)
                elif key in nums:
                    inputBar = inputBar[:inputIndex] + key + inputBar[inputIndex:]
                    inputIndex += 1
                elif key == "backspace":
                    if inputIndex != 0:
                        inputBar = inputBar[: inputIndex - 1] + inputBar[inputIndex:]
                        inputIndex -= 1
                        if inputIndex == -1:
                            inputIndex = 0
                elif key == "delete":
                    inputBar = inputBar[:inputIndex] + inputBar[inputIndex + 1 :]
                    if inputIndex >= len(inputBar):
                        inputIndex = len(inputBar)
                elif key == "space":
                    if (curIndex + 1) in selIndices:
                        inputBar = removeNumFromInput(str(curIndex + 1), inputBar)
                    if (curIndex + 1) not in selIndices:
                        selIndices.append(curIndex + 1)
                        if len(inputBar) != 0:
                            if inputBar[-1] == ",":
                                inputBar = inputBar + f"{curIndex+1},"
                            elif inputBar[-1] == "-":
                                inputBar = inputBar + f"{curIndex+1}"
                            else:
                                inputBar += f",{curIndex+1}"
                        else:
                            inputBar = f"{curIndex+1}"
                    inputIndex = len(inputBar)
            inputBar, selIndices = massSelectionInput_Parser(
                inputBar, len(selectionList)
            )
            # print(f"len: {len(inputBar)}, inputIndex+1: {inputIndex}")
            # input()
            if len(inputBar) < (inputIndex):
                inputIndex = inputIndex - 1
            curIndex, startIndex, endIndex = curIndexCalc(
                curIndex=curIndex,
                startIndex=startIndex,
                endIndex=endIndex,
                limit=limit,
                listLen=len(selectionList),
            )
            if key == "enter" and helpCond == False:
                selIndices = [i - 1 for i in selIndices]
                return selIndices
            if key == "h":
                helpCond = True
            else:
                helpCond = False
            # Delete printed lines in terminal
            delete_last_lines(delLineAmount + 1)

    def getKey():
        while True:
            key = keyboard.read_event()
            if key.event_type == "down":
                return key.name
