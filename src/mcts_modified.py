
from mcts_node import MCTSNode
from p2_t3 import Board, positions
from random import choice
from math import sqrt, log

num_nodes = 1000
explore_faction = 2.

def traverse_nodes(node: MCTSNode, board: Board, state, bot_identity: int):
    """ Traverses the tree until the end criterion are met.
    e.g. find the best expandable node (node with untried action) if it exist,
    or else a terminal node

    Args:
        node:       A tree node from which the search is traversing.
        board:      The game setup.
        state:      The state of the game.
        identity:   The bot's identity, either 1 or 2

    Returns:
        node: A node from which the next stage of the search can proceed.
        state: The state associated with that node

    """
    # Check if the current node is a terminal node
    if(board.is_ended(state)):
        return node, state
    
    # Check if the current node is a leaf node
    if(len(node.untried_actions) != len(node.child_nodes)):
        return node, state
    
    # Find the child with the highest UCT score
    max_node = None
    max_state = None
    max_score = 0
    for action, child in node.child_nodes.items():
        # Calculate child UCT score
        UCT_score = ucb(child, board.current_player(state) != bot_identity)

        # Set the child if it has a higher UCT score
        if UCT_score > max_score:
            max_node = child
            max_state = board.next_state(state, action)
            max_score = UCT_score
    
    # If the game ends at the child, current_player breaks
    if(max_state is None):
        return node, state
    
    # Take the node and action and recursively continue
    return traverse_nodes(max_node, board, max_state, board.current_player(max_state))

def expand_leaf(node: MCTSNode, board: Board, state):
    """ Adds a new leaf to the tree by creating a new child node for the given node (if it is non-terminal).

    Args:
        node:   The node for which a child will be added.
        board:  The game setup.
        state:  The state of the game.

    Returns:
        node: The added child node
        state: The state associated with that node

    """
    # Check if current node is a terminal node
    if(board.is_ended(state)):
        return node, state
    
    # Define the action that is to be taken from parent -> child
    action_taken = choice(node.untried_actions)

    # Make the new child node
    child_state = board.next_state(state, action_taken)
    child = MCTSNode(parent=node, parent_action=action_taken, action_list=board.legal_actions(child_state))

    # Update the parent's info
    node.child_nodes[action_taken] = child

    return child, child_state

def rollout(board: Board, state, bot_identity):
    
    curState = state
    subBoard = None
    grid = {}       # dict of subboard, storing owners
    valueGrid = {}  # dict of subboard, storing values
    turn = True     # is the simulation on this bot's turn
    actions = None  # legal actions

    while(not board.is_ended(curState)):

        if turn :                                               # if it is this bot's turn
            actions = board.legal_actions(curState)                 # populate all actions

            if len(board.legal_actions(curState)) > 9 :            # if the board is empty
                curState = board.next_state(curState, (1, 1, 1, 1))     # play the center, we are assuming this is the most valuable position

            else :                                                  # in all other cases
                # find the subboard we are in and populate it, also populate valueGrid
                subBoard = (actions[0][0], actions[0][1])               # assume the first legal action's 1st element is the column and 2nd element is the row, MIGHT BE REVERSED
                for x in range(3) :
                    for y in range(3) :
                        valueGrid[(x, y)] = 0
                        grid[(x, y)] = get_cell_owner(curState, subBoard[0], subBoard[1], x, y)
                        if grid[(x, y)] is not 0 :
                            valueGrid[(x, y)] = -1000

                # assign "basic" values to valueGrid, see function description
                valueGrid[(1, 1)] += 3
                for x in range(3) :
                    for y in range(3) :
                        if (x is 0 or x is 2) and (y is 0 or y is 2) :  # corner
                            valueGrid[(x, y)] += 1
                        if grid[(x, y)] is not 0 and grid[(x, y)] is not bot_identity : # a grid space is occupied by the opponent
                            for i in range(-1, 2) :
                                for j in range(-1, 2) :
                                    if (x + i <= 2) and (x + i >= 0) and (y + j <= 2) and (y + j >= 0) and (abs(x + i) is not abs(y + j)) :     # if the cell is in bounds and is not a diagonal or the space itself
                                        valueGrid[(x + i, y + j)] += 4
                
                # check to see if there is any row or column that has exactly 1 empty squares and 2 squares owned by a player
                # =================== im giving this a distinct break for readability ====================
                for i in range(3) :
                    zeroesR = 0     # zeroes in row
                    zeroesC = 0     # zeroes in column
                    for j in range(3) :     # count zeroes in row and column i
                        if grid[(i, j)] is 0 :
                            zeroesR += 1
                        if grid[(j, i)] is 0 :
                            zeroesC += 1
                    ones = 0
                    twos = 0
                    if zeroesR is 1 :       # if there is only 1 empty space in row i
                        for j in range(3) : # count X's and O's in row i
                            if grid[(i, j)] is 1 :
                                ones += 1
                            if grid[(i, j)] is 2 :
                                twos += 1
                        if ones is 2 or twos is 2 : # if there is 2 X's or O's in row i
                            for j in range(3) :
                                if grid[(i, j)] is 0 :  # find the empty space in row i
                                    valueGrid[(i, j)] += 7  # and increase its value accordingly
                    ones = 0
                    twos = 0
                    if zeroesC is 1 :       # if there is only 1 empty space in column i (this is the exact same as the row chunk)
                        for j in range(3) :
                            if grid[(j, i)] is 1 :
                                ones += 1
                            if grid[(j, i)] is 2 :
                                twos += 1
                        if ones is 2 or twos is 2 :
                            for j in range(3) :
                                if grid[(j, i)] is 0 :
                                    valueGrid[(i, j)] += 7

                    # diagonals are hardcoded, sorry
                    zeroes = 0
                    ones = 0
                    twos = 0
                    for i in range(3) : # top left to bottom right is easy
                        match grid[(i, i)] :
                            case 0:
                                zeroes += 1
                            case 1:
                                ones += 1
                            case 2:
                                twos += 1
                            case _:
                                pass        # should never run, will break everything
                    if zeroes is 1 and (ones is 2 or twos is 2) :
                        for i in range(3) :
                            if grid[(i, i)] is 0 :
                                valueGrid[(i, i)] += 7
                    zeroes = 0
                    ones = 0
                    twos = 0
                    for i in range(3) :
                        for j in range(2, -1) :
                            match grid[(i, j)] :
                                case 0:
                                    zeroes += 1
                                case 1:
                                    ones += 1
                                case 2:
                                    twos += 1
                                case _:
                                    pass        # should never run, will break everything
                    if zeroes is 1 and (ones is 2 or twos is 2) :
                        for i in range(3) :
                            for j in range(2, -1) :
                                if grid[(i, j)] is 0 :
                                    valueGrid[(i, j)] += 7
                # =========================================================================================
                # check subboard of each square, using a helper funciton to make this section not the most atrocious thing ever
                for a in range(3) :
                    for b in range(3) :
                        if grid[(a, b)] is 0 :
                            if confirm_sub_board(a, b, bot_identity, curState):
                                valueGrid[(a, b)] -= 10
                
                # find the grid spot with the best value
                x = 0
                y = 0
                value = -1000
                for i in range(3) :
                    for j in range(3) :
                        if valueGrid[(i, j)] > value :
                            x = i
                            y = j
                            value = valueGrid[(i, j)]
                # perform the action with the highest value
                intendedAction = (subBoard[0], subBoard[1], x, y)
                if board.is_legal(curState, intendedAction) :   # CHECK TO MAKE SURE IT'S LEGAL
                    curState = board.next_state(curState, intendedAction)
                else :
                    print("Something is very wrong :(")

        else :  # it is not this bot's turn
            curState = board.next_state(curState, choice(board.legal_actions(curState))) # assume the other player plays randomly

        # reset values, switch perspectives
        actions = None
        subBoard = None
        grid = {}
        valueGrid = {}
        turn = not turn

    return(curState)

def confirm_sub_board(boardx, boardy, bot_identity, state) :

    bad = 0
    grid = {}

    for a in range(3):
        for b in range(3):
            grid[(a, b)] = get_cell_owner(state, boardx, boardy, a, b)

    match bot_identity:
        case 1:
            bad = 2
        case 2:
            bad = 1

    zeroesD1 = 0
    badD1 = 0
    zeroesD2 = 0
    badD2 = 0
    for i in range(3) :
        zeroesR = 0     # zeroes in row
        zeroesC = 0     # zeroes in column
        badR = 0
        badC = 0

        for j in range(3) :     # count zeroes and bads in row and column i
            if grid[(i, j)] is 0 :
                zeroesR += 1
            if grid[(j, i)] is 0 :
                zeroesC += 1
            if grid[(i, j)] is bad :
                badR += 1
            if grid[(j, i)] is bad :
                badC += 1

        match grid[(i, i)]:     # count zeroes and bads in diag top left to bottom right
            case 0:
                zeroesD1 += 1
            case bad:
                badD1 += 1
        
        if (zeroesR is 1 and badR is 2) or (zeroesC is 1 and badC is 2):    # if a row or column has 1 empty and 2 bads
            return(True)
        
    for i in range(3):
        for j in range(2, -1):
            match grid[(i, j)]:
                case 0:
                    zeroesD2 += 1
                case bad:
                    badD2 += 1

    if (zeroesD1 is 1 and badD1 is 2) or (zeroesD2 is 1 and badD2 is 2):    # if a diagonal has 1 empty and 2 bads
        return(True)
    
    return(False)   # there is no move an opponent will win currently from this board

def get_cell_owner(state, board_r, board_c, pos_r, pos_c):
    board_index = 3 * board_r + board_c
    p1_bitmask = state[2*board_index]
    p2_bitmask = state[2*board_index+1]
    is_p1 = (p1_bitmask & positions[(pos_r, pos_c)]) > 0
    is_p2 = (p2_bitmask & positions[(pos_r, pos_c)]) > 0
    if is_p1:
        return 1
    if is_p2:
        return 2
    return 0

def backpropagate(node: MCTSNode|None, won: bool):
    """ Navigates the tree from a leaf node to the root, updating the win and visit count of each node along the path.

    Args:
        node:   A leaf node.
        won:    An indicator of whether the bot won or lost the game.

    """
    # Check if node is root
    if(node.parent is None):
        node.visits += 1
        return
    
    # Update the node's statistics otherwise
    node.visits += 1
    if(won):
        node.wins += 1
    
    # Recursively backpropagate up the tree
    backpropagate(node.parent, won)
    return

def ucb(node: MCTSNode, is_opponent: bool):
    """ Calcualtes the UCB value for the given node from the perspective of the bot

    Args:
        node:   A node.
        is_opponent: A boolean indicating whether or not the last action was performed by the MCTS bot
    Returns:
        The value of the UCB function for the given node
    """
    # Calculate the child's win rate
    exploit = node.wins / node.visits

    # If opponent, calculate the opponent's win rate
    if(is_opponent):
        exploit = 1 - exploit

    # Calculate the inside of the root
    explore = log(node.parent.visits) / node.visits

    # Combine the exploitation and exploration calculations
    ucb = exploit + (explore_faction * sqrt(explore))

    return ucb

def get_best_action(root_node: MCTSNode):
    """ Selects the best action from the root node in the MCTS tree

    Args:
        root_node:   The root node
    Returns:
        action: The best action from the root node
    
    """
    # Find the child with the most wins
    best_action = None
    best_score = 0

    for action, child in root_node.child_nodes.items():
        if(child.visits > best_score):
            best_score = child.visits
            best_action = action

    return best_action

def is_win(board: Board, state, identity_of_bot: int):
    # checks if state is a win state for identity_of_bot
    outcome = board.points_values(state)
    assert outcome is not None, "is_win was called on a non-terminal state"
    return outcome[identity_of_bot] == 1

def think(board: Board, current_state):
    """ Performs MCTS by sampling games and calling the appropriate functions to construct the game tree.

    Args:
        board:  The game setup.
        current_state:  The current state of the game.

    Returns:    The action to be taken from the current state

    """
    bot_identity = board.current_player(current_state) # 1 or 2
    root_node = MCTSNode(parent=None, parent_action=None, action_list=board.legal_actions(current_state))

    for _ in range(num_nodes):
        state = current_state
        node = root_node

        # Do MCTS - This is all you!
        node, state = traverse_nodes(node, board, state, board.current_player(state))
        node, state = expand_leaf(node, board, state)
        backpropagate(node, is_win(board, rollout(board, state, bot_identity), bot_identity))

    # Return an action, typically the most frequently used action (from the root) or the action with the best
    # estimated win rate.
    best_action = get_best_action(root_node)
    
    # print(f"Action chosen: {best_action}")
    return best_action
