import asyncio
import botinfo
import cairosvg
import chess
import chess.svg
import discord
import io
import logging

client = discord.Client()
logging.basicConfig(level=logging.INFO)

checkHighlight = None

def boardToPng(board):
    checkHighlight = None # initialize highlight in case no check
    for square in chess.SQUARES: # loop over all squares to find king
        piece = board.piece_at(square)
        if piece != None:
            if (piece.color == board.turn and 
                piece.piece_type == chess.KING and
                board.is_attacked_by(not board.turn, square)):
    
                checkHighlight = square # if the king is in check, highlight
    
    svgString = chess.svg.board(board=board, 
                                coordinates=False,
                                check=checkHighlight)

    return cairosvg.svg2png(bytestring=svgString.encode('utf-8'))
    
@client.event
async def on_message(message):
    commandArray = message.content.split(" ", 1)
    if len(commandArray) == 1: # Quick hack to keep python happy
        command = commandArray[0]
        tail = ""
        args = []
    else:
        command, tail = commandArray
        args = tail.split(" ")

    # By the end of the above block, command is the command, tail is the
    # trailing data, and args is a list containing each word after the
    # command.

    if command == ">fentopng":
        try:
            board = chess.Board(tail) # gen board from fen
            pngData = boardToPng(board)
            with io.BytesIO(pngData) as pngBytes:
                await client.send_file(message.channel,
                                       io.BytesIO(pngData),
                                       filename="board.png")
        except ValueError: # chess.Board() throws ValueError if fen is invalid
            await client.send_message(message.channel, "Invalid FEN")

client.run(botinfo.token)
