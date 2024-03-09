import styles from "../styles/console.module.css";
import { Autocomplete, Button, Group, ScrollArea, Stack } from "@mantine/core";
import { consoleToText, getCommands } from "../modules/nimplant";
import { FaTerminal } from "react-icons/fa";
import { getHotkeyHandler, useFocusTrap, useMediaQuery } from "@mantine/hooks";
import ExecuteAssemblyModal from "./modals/Cmd-Execute-Assembly";
import InlineExecuteModal from "./modals/Cmd-Inline-Execute";
import React, { useEffect, useRef, useState } from "react";
import ShinjectModal from "./modals/Cmd-Shinject";
import UploadModal from "./modals/Cmd-Upload";

type ConsoleType = {
  allowInput? : boolean
  consoleData : any
  disabled? : boolean
  guid?: string
  inputFunction?: (guid: string, command: string) => void
}

function Console({ allowInput, consoleData, disabled, guid, inputFunction }: ConsoleType) {
  const largeScreen = useMediaQuery('(min-width: 800px)');

  // Define viewport and stickyness as state
  const consoleViewport = useRef<HTMLDivElement>();
  const [sticky, setSticky] = useState(true)
  
  // Trap focus on command input by default
  const focusTrapRef = useFocusTrap();
  
  // Define states
  const [autocompleteOptions, setAutocompleteOptions] = useState<string[]>([]);
  const [dropdownOpened, setDropdownOpened] = useState(false);
  const [enteredCommand, setEnteredCommand] = useState('');
  const [historyPosition, setHistoryPosition] = useState(0);
  const [modalExecAsmOpened, setModalExecAsmOpened] = useState(false);
  const [modalInlineExecOpened, setModalInlineExecOpened] = useState(false);
  const [modalshinjectOpened, setModalShinjectOpened] = useState(false);
  const [modalUploadOpened, setModalUploadOpened] = useState(false);

  // Define dynamic autocomplete options
  const {commandList, commandListLoading, commandListError} = getCommands()

  // Define a utility function to handle command and clear the input field
  const handleSubmit = () => {
    if (inputFunction === undefined || guid === undefined) return;

    if (autocompleteOptions.length === 0) setDropdownOpened(false);
    else if (dropdownOpened) return;

    // Handle 'modal commands'
    if (enteredCommand === 'execute-assembly') {
      setModalExecAsmOpened(true);
    }
    else if (enteredCommand === 'inline-execute') {
      setModalInlineExecOpened(true);
    }
    else if (enteredCommand === 'shinject') {
      setModalShinjectOpened(true);
    }
    else if (enteredCommand === 'upload') {
      setModalUploadOpened(true);
    }
    
    // Handle other commands
    else {
      inputFunction(guid, enteredCommand);
    }

    // Clear the input field
    setHistoryPosition(0);
    setEnteredCommand('');
  }

  // Define a utility function to handle command history with up/down keys
  const handleHistory = (direction: number) => {
    const commandHistory = consoleData.filter((i:any) => i.taskFriendly !== null);
    const histLength : number = commandHistory.length
    var   newPos     : number = historyPosition + direction

    // Only allow history browsing when there is history and the input field is empty or matches a history entry
    if (histLength === 0) return;
    if (!commandHistory.some((i:any) => i.taskFriendly == enteredCommand) && enteredCommand !== '') return;
    
    // Trigger history browsing only with the 'up' direction
    if (historyPosition === 0 && direction === 1) return;
    if (historyPosition === 0 && direction === -1) newPos = histLength;
    
    // Handle bounds, including clearing the input field if the end is reached
    if (newPos < 1) newPos = 1;
    else if (newPos > histLength) {
      setHistoryPosition(0);
      setEnteredCommand('');
      return;
    };

    setHistoryPosition(newPos);
    setEnteredCommand(commandHistory[newPos-1]['taskFriendly']);
  }

  // Set hook for handling manual scrolling
  const handleScroll = (pos: { x: number; y: number; }) => {
    if (consoleViewport.current?.clientHeight === undefined) return;
    if (pos.y + consoleViewport.current?.clientHeight === consoleViewport.current?.scrollHeight){
      setSticky(true);
    } else {
      setSticky(false);
    }
  }

  // Define 'sticky' functionality to only auto-scroll if user was already at bottom
  const scrollToBottom = () => {
    consoleViewport.current?.scrollTo({ top: consoleViewport.current?.scrollHeight, behavior: 'smooth' });
  }
  
  // Scroll on new input if sticky
  useEffect(() => {
    if (sticky) scrollToBottom();
  })

  // Recalculate autocomplete options
  useEffect(() => {

    const getCompletions = (): string[] => {
      if (enteredCommand === '') return [];
  
      var completionOptions: string[] = [];
  
      // Add base command completions
      if (!commandListLoading && !commandListError) {
        completionOptions = commandList.map((a:any) => a['command'])
      }
      
      // Add history completions, ignore duplicates
      Object.keys(consoleData).forEach((key) => {
        if (consoleData[key]['taskFriendly'] !== null) {
          var value : string = consoleData[key]['taskFriendly']
          if (!completionOptions.includes(value)){
            completionOptions.push(value)
          }
          
        }
      })
  
      return completionOptions.filter((o) => o.startsWith(enteredCommand) && o != enteredCommand);
    }

    setAutocompleteOptions(getCompletions());
  }, [enteredCommand, commandListLoading, commandListError, consoleData, commandList])

  return (
    <Stack ml={largeScreen ? "xl" : "lg"} mr={largeScreen ? 40 : 35} mt="xl" gap="xs"
      style={{
        height: 'calc(100vh - 285px)',
        display: 'flex',
      }}
    >
          {/* Modals */}
          <ExecuteAssemblyModal modalOpen={modalExecAsmOpened} setModalOpen={setModalExecAsmOpened} npGuid={guid} />
          <InlineExecuteModal modalOpen={modalInlineExecOpened} setModalOpen={setModalInlineExecOpened} npGuid={guid} />
          <ShinjectModal modalOpen={modalshinjectOpened} setModalOpen={setModalShinjectOpened} npGuid={guid} />
          <UploadModal modalOpen={modalUploadOpened} setModalOpen={setModalUploadOpened} npGuid={guid} />
        
          {/* Code view window */}
          <Group m={0} p={0} grow 
            style={{
              fontSize: '14px',
              width: '100%',
              height: 'calc(100% - 40px)',
              border: '1px solid',
              borderColor: 'var(--mantine-color-gray-4)',
              borderRadius: '4px',
            }}
          >
              <ScrollArea
                viewportRef={consoleViewport as any}
                onScrollPositionChange={handleScroll}
                style={{
                  fontSize: largeScreen ? '14px' : '12px',
                  padding: largeScreen ? '14px' : '6px',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  color: 'var(--mantine-color-gray-8)',
                  backgroundColor: 'var(--mantine-color-gray-0)',
                  height: '100%',
                  flex: '1',
                }}
              >
                  {!consoleData ? "Loading..." : consoleToText(consoleData)}
              </ScrollArea>
          </Group>

        {/* Command input field */}
        {allowInput ? (
          <Group 
          style={{
            flex: '0',
          }}>
            <Autocomplete 
              data={autocompleteOptions}
              disabled={disabled}
              leftSection={<FaTerminal size={14} />}
              onChange={setEnteredCommand}
              onDropdownClose={() => setDropdownOpened(false)}
              onDropdownOpen={() => setDropdownOpened(true)}
              placeholder={disabled ? "Nimplant is not active" : "Type command here..."}
              ref={focusTrapRef}
              value={enteredCommand}
              onKeyDown={getHotkeyHandler([
                ['Enter', handleSubmit],
                ['Tab', () => autocompleteOptions.length > 0 && setEnteredCommand(autocompleteOptions[0])],
                ['ArrowUp', () => handleHistory(-1)],
                ['ArrowDown', () => handleHistory(1)],
              ])}
              style={{
                flex: '1',
              }}
            />
            <Button disabled={disabled} onClick={handleSubmit}>Run command</Button>
          </Group>
        ) : null}

    </Stack>
  )
}

export default Console