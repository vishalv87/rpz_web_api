# Checks two different FEN-strings, and determines the move that was made using only standard python modules and functions (and returns in UCI-format)

# The original purpose of this code is to help determine the move made based on only FEN-data.
# The chessboard sends a continuous stream
# of current positions in the form of FEN, and this code determines what move was made using
# that FEN-data by comparing it to the last
# known board position.

# Keep in mind that (althrough some simple checks are introduced) no actual validation
# is being done in this code.
# You can introduce a package like
# python-chess or a stockfish wrapper to help validate the FEN-data

intList = ["1", "2", "3", "4", "5", "6", "7", "8"]
letterList = ["a", "b", "c", "d", "e", "f", "g", "h"]


def fendiff(position1, position2):
    # Iterator starts from 8, since the backrank (top of the bord) is also the top of the list, which is row 8
    rowIteratorInt = 8
    move = []
    simplifiedX = []
    simplifiedY = []
    for x, y in zip(_fenPass(position1), _fenPass(position2)):
        # Move down the board, minus 1 per loop
        rowIteratorInt -= 1
        if x != y:
            newXString = ""

            # In order to make processing the data easier, this makes sure that the string length is always 8 by replacing numbers
            # with a certain amount of zeroes. That way the string is always 8 long and a "0" automatically represents an empty space.
            for c in x:
                if c in intList:
                    newXString += "0" * int(c)
                else:
                    newXString += c
            simplifiedX.append(newXString)

            newYString = ""
            for d in y:
                if d in intList:
                    newYString += "0" * int(d)
                else:
                    newYString += d
            simplifiedY.append(newYString)
            columnIteratorInt = 0
            for a, b in zip(newXString, newYString):
                columnIteratorInt += 1
                if a != b:
                    # if b == "0", that means that spot on the chessboard ended up empty in the new position. That means that that was the original
                    # place a piece was standing on, so that coordinate comes first in the notation. Therefore it must be inserted instead of appended.
                    if b == "0":
                        move.insert(
                            0,
                            f"{letterList[columnIteratorInt - 1]}{rowIteratorInt + 1}",
                        )

                    # If b is anything but "0", that means a piece now stands on that position. That means that a piece moved there.
                    else:
                        move.append(
                            f"{letterList[columnIteratorInt - 1]}{rowIteratorInt + 1}"
                        )

    # Compile the list into a string
    move = "".join(move)

    # If the length of the move is already equal to 4 (or 5 in the case of promotion), no "special" move or capture was made. Therefore, just return the move as-is
    if len(move) == 4:
        # Check for a potential promotion.
        if move[1] == "7" and int(move[3]) > int(move[1]):
            # Case for a potential white pawn
            if simplifiedX[1][letterList.index(move[0])] == "P":
                return move + simplifiedY[0][letterList.index(move[2])].lower()

        if move[1] == "2" and int(move[3]) < int(move[1]):
            # Case for a potential black pawn
            if simplifiedX[0][letterList.index(move[0])] == "p":
                return move + simplifiedY[1][letterList.index(move[2])]

        return move

    # En passant cases: Capturing to the left or the right makes a difference in the
    # order using this function, so to rectify this compare the first and the third char
    # with eachother to determine which way a capture was made. There has to be a way
    # to make this prettier, so if you have feedback let me know

    if len(move) == 6:
        # The size of the move is only 6 if en passant occured.
        if move[0] == move[4]:
            return move[2:]

        if move[2] == move[4]:
            return move[:2] + move[-2:]

    # Special cases for castling, since castling does not leave an empty on the first space and moves two pieces at the same time.
    # Honestly, if anyone finds a better way to do this let me know @klepv1nk. However, since castling positions are always the same
    # anyways, this solution works (i don't imagine this working for chess960 though so again please, feel free to expand on this code).

    # Case for kingside castling (white)
    if move == "h1e1f1g1":
        return "e1g1"
    # Case for queenside castling (white)
    if move == "e1a1c1d1":
        return "e1c1"
    # Case for kingside castling (black)
    if move == "h8e8f8g8":
        return "e8g8"
    # Case for queenside castling (black)
    if move == "e8a8c8d8":
        return "e8c8"


def _fenPass(fen):
    fen = fen.split(" ")[0].split("/")
    if len(fen) != 8:
        raise ValueError(
            "expected 8 rows in position part of fen: {0}".format(repr(fen))
        )
    for fenPart in fen:
        field_sum = 0
        previous_was_digit, previous_was_piece = False, False
        for c in fenPart:
            if c in intList:
                if previous_was_digit:
                    raise ValueError(
                        "two subsequent digits in position part of fen: {0}".format(
                            repr(fen)
                        )
                    )
                field_sum += int(c)
                previous_was_digit = True
                previous_was_piece = False
            elif c == "~":
                if not previous_was_piece:
                    raise ValueError(
                        "~ not after piece in position part of fen: {0}".format(
                            repr(fen)
                        )
                    )
                previous_was_digit, previous_was_piece = False, False
            elif c.lower() in ["p", "n", "b", "r", "q", "k"]:
                field_sum += 1
                previous_was_digit = False
                previous_was_piece = True
            else:
                raise ValueError(
                    "invalid character in position part of fen: {0}".format(repr(fen))
                )
        if field_sum != 8:
            raise ValueError(
                "expected 8 columns per row in position part of fen: {0}".format(
                    repr(fen)
                )
            )
    return fen


move1 = fendiff(
    "r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/R3K2R w KQkq - 1 12",
    "r3kb1r/p2nqppp/5n2/1B2p1B1/4P3/1Q6/PPP2PPP/2KR3R b kq - 2 12",
)
print(move1)
