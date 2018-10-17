#!/usr/bin/python3
import sys

class FiniteStateAutomata():
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
                
    def Manager(self):
        prefixFunc  = self.Prefix()

        fsa = self.InitFSA()
        self.FillWithFirstState(fsa)
        self.AddTransitionStates(fsa)
        self.CorrectFsaForPrefixes(fsa, prefixFunc)

        numOfPatternOccurrences = self.EmulateFsa(fsa)

        self.printFSA(fsa, prefixFunc, numOfPatternOccurrences)

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

    def InitFSA(self):
        alphabetSize = len(self.alphabet)
        numOfStates  = len(self.pattern) + 1 #adding "additional" accepting state

        wight, height = alphabetSize, numOfStates
        fsa = [[0 for x in range(wight)] for y in range(height)]
        
        return fsa

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
        # in any state that it will be at least in state 1 )
        for stateIndex in range(len(fsa)):
            for innerArrayIndex in range(len(fsa[0])):
                fsa[stateIndex][innerArrayIndex] = firstState[innerArrayIndex]

        return fsa

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

    def CorrectFsaForPrefixes(self, fsa, prefixFunc):
        for stateToUpdate, prefixfuncValue in enumerate(prefixFunc):
            if prefixfuncValue is not 0:
                stateToUpdate += 1 #bc of the algorithm of prefixFunction
                self.updateStateFromPrefixFunc(prefixfuncValue, stateToUpdate, fsa)            
        
    def updateStateFromPrefixFunc(self, prefixfuncValue, stateToUpdate, fsa):
        for symbolState in range(len(fsa[0])):
            if fsa[stateToUpdate][symbolState] < fsa[prefixfuncValue][symbolState]:
                fsa[stateToUpdate][symbolState] = fsa[prefixfuncValue][symbolState]

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

automata = FiniteStateAutomata()
automata.Manager()