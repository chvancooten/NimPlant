import { Button, FileButton, Modal, NumberInput, SimpleGrid, Space, Text } from "@mantine/core"
import { Dispatch, SetStateAction, useState } from "react";
import { FaBullseye, FaTerminal } from "react-icons/fa"
import { submitCommand, uploadFile } from "../../modules/nimplant";


interface IProps {
    modalOpen: boolean;
    setModalOpen: Dispatch<SetStateAction<boolean>>;
    npGuid: string | undefined;
}

function ShinjectModal({ modalOpen, setModalOpen, npGuid }: IProps) {
    const [scFile, setScFile] = useState<File | null>(null);
    const [targetPid, setTargetPid] = useState<number | undefined>(undefined);
    const [submitLoading, setSubmitLoading] = useState(false);

    const submit = () => {
        // Check if a file is selected
        if (!scFile || scFile === null) {
            return;
        }

        // Upload the file
        setSubmitLoading(true);
        uploadFile(scFile, callbackCommand, callbackClose);
    };

    const callbackCommand = (uploadPath: string) => {       
        // Handle the execute-assembly command
        submitCommand(String(npGuid), `shinject ${targetPid} "${uploadPath}"`, callbackClose);
    };

    const callbackClose = () => {
        // Reset state
        setModalOpen(false);
        setScFile(null);
        setTargetPid(undefined);
        setSubmitLoading(false);
    };

    return (
        <Modal
            opened={modalOpen}
            onClose={() => setModalOpen(false)}
            title={<b>Shinject: Inject and execute shellcode</b>}
            size="auto"
            centered
        >
            <Text>Execute shellcode in a selected target process using dynamic invocation.</Text>

            <Space h='xl' />

            <SimpleGrid cols={1}>

            {/* File selector */}
            <FileButton onChange={setScFile}>
                {(props) => <Button color={"gray"} {...props}>
                    {scFile ? "File: " + scFile.name  : "Select shellcode file"}
                </Button>}
            </FileButton>
            
            {/* PID argument */}
            <NumberInput 
                placeholder="Target Process (PID)"
                value={targetPid}
                leftSection={<FaBullseye />}
                onChange={(value) => setTargetPid(Number(value))}
                min={0}
            />

            </SimpleGrid>

            <Space h='xl' />

            {/* Submit button */}
            <Button 
                onClick={submit}
                leftSection={<FaTerminal />}
                style={{width: '100%'}}
                loading={submitLoading}
            >
                Execute
            </Button>
        </Modal>
    )
}

export default ShinjectModal