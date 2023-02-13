import { Autocomplete, Button, Group, ScrollArea, Stack } from "@mantine/core";
import { FaTerminal } from "react-icons/fa";
import { consoleToText, getCommands } from "../modules/nimplant";
import { getHotkeyHandler, useFocusTrap, useMediaQuery } from "@mantine/hooks";
import React, { useEffect, useRef, useState } from "react";
import InlineExecuteModal from "./modals/Cmd-Inline-Execute";
import ExecuteAssemblyModal from "./modals/Cmd-Execute-Assembly";
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
  const [modalInlineExecOpened, setModalInlineExecOpened] = useState(false);
  const [modalExecAsmOpened, setModalExecAsmOpened] = useState(false);
  const [modalUploadOpened, setModalUploadOpened] = useState(false);

  // Define dynamic autocomplete options
  const {commandList, commandListLoading, commandListError} = getCommands()

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

  // Define a utility function to handle command and clear the input field
  const handleSubmit = () => {
    if (inputFunction === undefined || guid === undefined) return;

    if (autocompleteOptions.length === 0) setDropdownOpened(false);
    else if (dropdownOpened) return;

    // Handle 'modal commands'
    if (enteredCommand === 'inline-execute') {
      setModalInlineExecOpened(true);
    }
    else if (enteredCommand === 'execute-assembly') {
      setModalExecAsmOpened(true);
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
    setAutocompleteOptions(getCompletions());
  }, [enteredCommand, commandListLoading, consoleData])

  return (
    <Stack ml={largeScreen ? "xl" : "lg"} mr={largeScreen ? 40 : 35} mt="xl" spacing="xs"
      sx={() => ({
        height: 'calc(100vh - 275px)',
        display: 'flex',
      })}
    >
          {/* Modals */}
          <InlineExecuteModal modalOpen={modalInlineExecOpened} setModalOpen={setModalInlineExecOpened} npGuid={guid} />
          <ExecuteAssemblyModal modalOpen={modalExecAsmOpened} setModalOpen={setModalExecAsmOpened} npGuid={guid} />
          <UploadModal modalOpen={modalUploadOpened} setModalOpen={setModalUploadOpened} npGuid={guid} />
        
          {/* Code view window */}
          <Group m={0} p={0} grow 
            sx={(theme) => ({
              fontSize: '14px',
              width: '100%',
              flex: '1',
              border: '1px solid',
              borderColor: theme.colors.gray[4],
              borderRadius: '4px',
              minHeight: 0,
            })}>
              <ScrollArea
                viewportRef={consoleViewport as any}
                onScrollPositionChange={handleScroll}
                sx={(theme) => ({
                  fontSize: largeScreen ? '14px' : '12px',
                  padding: largeScreen ? '14px' : '6px',
                  whiteSpace: 'pre-wrap',
                  fontFamily: 'monospace',
                  color: theme.colors.gray[8],
                  backgroundColor: theme.colors.gray[0],
                  height: '100%',
                })}
              >
                  {!consoleData ? "Loading..." : consoleToText(consoleData)}
              </ScrollArea>
          </Group>

        {/* Command input field */}
        <Group hidden={!allowInput}
        sx={() => ({
          flex: '0',
        })}>
          <Autocomplete 
            data={autocompleteOptions}
            disabled={disabled}
            icon={<FaTerminal size={14} />}
            onChange={setEnteredCommand}
            onDropdownClose={() => setDropdownOpened(false)}
            onDropdownOpen={() => setDropdownOpened(true)}
            placeholder={disabled ? "Nimplant is not active" : "Type command here..."}
            ref={focusTrapRef}
            switchDirectionOnFlip={true}
            value={enteredCommand}
            onKeyDown={getHotkeyHandler([
              ['Enter', handleSubmit],
              ['ArrowUp', () => handleHistory(-1)],
              ['ArrowDown', () => handleHistory(1)],
            ])}
            sx={() => ({
              flex: '1',
            })}
          />
          <Button disabled={disabled} onClick={handleSubmit}>Run command</Button>
        </Group>

    </Stack>
  )
}

export default Console