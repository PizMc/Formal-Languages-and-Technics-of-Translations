#!/usr/bin/python3
import sys #needed for stdin from console - used in __init__

###############################################################################
# 
# @name: FiniteStateAutomata
# @brief: provides functions and outputs for finite state machine for pattern searching
# @date: 15.10.2018
#
###############################################################################
class FiniteStateAutomata():
###############################################################################
# @name: __init__
# @brief: setting class global variables from stdin
#        >self.alphabet
#        >self.text
#        >self.pattern 
###############################################################################
    def __init__(self):
        if len(sys.argv) !=3:
            print("Require pattern, and text as 2 additional arguments")
            exit()
        else:
            if len(sys.argv[1]) > 1000000:
                print("Pattern is to big")
                exit()
            else:
                self.pattern  = sys.argv[1]
                tmpAlphabet   = list(set(self.pattern))
                tmpAlphabet.sort()
                self.alphabet = tmpAlphabet
                self.text = sys.argv[2]

###############################################################################
# @name: Manager
# @brief: Creates and manage workflow of creating and usage of fsa
###############################################################################
    def Manager(self):
        prefixFunc  = self.Prefix()

        fsa = self.InitFSA()
        self.FillWithFirstState(fsa)
        self.AddTransitionStates(fsa)
        self.CorrectFsaForPrefixes(fsa, prefixFunc)

        numOfPatternOccurrences = self.EmulateFsa(fsa)

        self.printFSA(fsa, prefixFunc, numOfPatternOccurrences)

###############################################################################
# @name: Prefix
# @brief: Creates prefix function that search for prefix in suffix of pattern
# @example: pattern: ababc if we are in state 4 and dont get 'c' then if we get
#           'a' we can go to state 2->3. And that knowledge provides prefix func.
# @ret: prefix function - 1D array with states transition in case of failure
###############################################################################
    def Prefix(self):
        pattern = self.pattern
        prefixArray = [0] * len(pattern)

        prefixH = 0
        suffixH = 1
        while suffixH < len(pattern):
            while prefixH > 0 and pattern[prefixH] != pattern[suffixH]:
                prefixH = prefixArray[prefixH - 1]
            
            if pattern[prefixH] == pattern[suffixH]:
                prefixH += 1
                prefixArray[suffixH] = prefixH

            #else:# prefixHead != suffixHead:
            #    prefixArray[suffixHead_id] = 0
            suffixH += 1

        return prefixArray    

###############################################################################
# @name: InitFSA
# @brief: Creates fsa - finite state automata
# @ret: fsa - 2D array of fsa first columns represents symbols from self.alphabet
#       rows represents each state
###############################################################################
    def InitFSA(self):
        alphabetSize = len(self.alphabet)
        numOfStates  = len(self.pattern) + 1 #adding "additional" accepting state

        wight, height = alphabetSize, numOfStates
        fsa = [[0 for x in range(wight)] for y in range(height)]
        
        return fsa

###############################################################################
# @name: FillWithFirstState
# @brief: Fills all states with computed first state for fsa.
#         If 'bad' symbol (not expected as the next symbol in pattern)
#         but this symbol will be first in pattern, then we should go to state 2
#         as we would already be in state 0.
#         !!! This is not provided from prefix function !!!
# @param[in]: fsa - 2D array representing fsa
# @param[out]: fsa with initialised states
# @ret: fsa - 2D array of fsa first columns represents symbols from self.alphabet
#       rows represents each state
###############################################################################         
    def FillWithFirstState(self, fsa):
        pattern = self.pattern
        
        index = 0
        for symbol in self.alphabet:
            if symbol is pattern[0]:
                break
            index += 1

        firstState = fsa[0]
        firstState[index] = 1 #now first state is complete

        #Filling states with first state
        # (if first letter will be "Wrong" input 
        # in any state - then if it is 1st symbol of pattern then 
        # it should be in state 1. 0 is state for other symbols)
        for stateIndex in range(len(fsa)):
            for innerArrayIndex in range(len(fsa[0])):
                fsa[stateIndex][innerArrayIndex] = firstState[innerArrayIndex]

###############################################################################
# @name: AddTransitionStates
# @brief: Adds basic traditions states from pattern
# @example: pattern ab state 0 goes to state 1 with 'a'
# param[in]: fsa - 2D array representing fsa
# param[out]: fsa with added transitions states which can over write filled with
#             first state - what is expected/predicted
# @ret: fsa - 2D array of fsa first columns represents symbols from self.alphabet
#       rows represents each state
###############################################################################
    def AddTransitionStates(self, fsa):
        symbolsDict = {}
        for index, symbol in enumerate(self.alphabet):
            symbolsDict[symbol] = index
            index += 1

        #for stateIndex, state in enumerate(FSA):
        stateIndex = 0
        for stateIndex in range(len(fsa)-1):
            symbol = self.pattern[stateIndex]
            symbolId = symbolsDict[symbol]

            fsa[stateIndex][symbolId] = stateIndex + 1

###############################################################################
# @name: CorrectFsaForPrefixes
# @brief: Using prefix functions corrects fsa for known and all states that
#         bucks sup - occur before - as prefix 
# param[in]: fsa - 2D array representing fsa
# param[out]: fsa with corrected transitions states
# param[in]: prefixFunc - 1D array that represent prefix function
###############################################################################
    def CorrectFsaForPrefixes(self, fsa, prefixFunc):
        for stateToUpdate, prefixfuncValue in enumerate(prefixFunc):
            if prefixfuncValue is not 0:
                stateToUpdate += 1 #bc of the algorithm of prefixFunction
                self.UpdateStateFromPrefixFunc(prefixfuncValue, stateToUpdate, fsa)            
        
###############################################################################
# @name: UpdateStateFromPrefixFunc
# @brief: updates state to correct
# @usage: by function CorrectFsaForPrefixes
# param[in]: prefixfuncValue - value - state that prefix function point to
# param[in]: stateToUpdate - state that we are updating right now
# param[in]: fsa - 2D array representing fsa
# param[out]: fsa with corrected transitions states
###############################################################################
    def UpdateStateFromPrefixFunc(self, prefixfuncValue, stateToUpdate, fsa):
        for symbolState in range(len(fsa[0])):
            if fsa[stateToUpdate][symbolState] < fsa[prefixfuncValue][symbolState]:
                fsa[stateToUpdate][symbolState] = fsa[prefixfuncValue][symbolState]

###############################################################################
# @name: EmulateFsa
# @brief: Emulates fsa - fully working finite state machine
# param[in]: fsa - 2D array representing fsa
# @return: number of times that pattern occurred in given text
###############################################################################
    def EmulateFsa(self, fsa):
        inputText = self.text
        alphabet = self.alphabet

        counter = 0
        acceptingStateId = len(fsa) - 1 #-1 bc. arrays are indexing from 0
        state = 0
        for symbol in inputText:
            if symbol in alphabet:
                symbolColumn = alphabet.index(symbol)
                state = fsa[state][symbolColumn]
            else:
                state = 0

            if state == acceptingStateId:
                counter += 1
    
        return counter

###############################################################################
# @name: printFSA
# @brief: Prints out pattern and states and fsa
# param[in]: fsa - 2D array representing fsa
# param[in]: prefixFunction - 1D array that represent prefix function
# param[in]: numOfPatternOccurrences - umber of times that pattern occurred
###############################################################################
    def printFSA(self, fsa, prefixFunction, numOfPatternOccurrences):
        print()
        print("Pattern:", self.pattern, "\n")

        print("p: ", end='')
        for p in range(len(self.pattern)):
            print(self.pattern[p], " ", end='')
        print()
        print("i: ", end='')
        for i in range(len(self.pattern)):
            print(i, " ", end='')
        print()
        print("π: ", end='')
        for pi in range(len(prefixFunction)):
            print(prefixFunction[pi], " ", end='')
        print("\n")
        

        print("   ", end='')
        for symbol in self.alphabet:
            print(symbol, " ", end='')
        print()
        for stateIndex, table in enumerate(fsa):
            if stateIndex < len(self.pattern):
                print(stateIndex, table, self.pattern[stateIndex])
            else:
                print(stateIndex, table, "Accept")

        print("\nNumber of pattern occurrences:", numOfPatternOccurrences)
        print()

#usage example
automata = FiniteStateAutomata()
automata.Manager()
