import { Button, Chip, FileButton, Flex, Input, Modal, SimpleGrid, Space, Text } from "@mantine/core"
import { Dispatch, SetStateAction, useState } from "react";
import { FaTerminal } from "react-icons/fa"
import { submitCommand, uploadFile } from "../../modules/nimplant";


interface IProps {
    modalOpen: boolean;
    setModalOpen: Dispatch<SetStateAction<boolean>>;
    npGuid: string | undefined;
}

function ExecuteAssemblyModal({ modalOpen, setModalOpen, npGuid }: IProps) {
    const [assemblyFile, setAssemblyFile] = useState<File | null>(null);
    const [assemblyArguments, setAssemblyArguments] = useState("");
    const [patchAmsi, setPatchAmsi] = useState(true);
    const [patchEtw, setPatchEtw] = useState(true);
    const [submitLoading, setSubmitLoading] = useState(false);

    const submit = () => {
        // Check if a file is selected
        if (!assemblyFile || assemblyFile === null) {
            return;
        }
        
        // Upload the file
        setSubmitLoading(true);
        uploadFile(assemblyFile, callbackCommand, callbackClose);
    };

    const callbackCommand = (uploadPath: string) => {
        // Parse the parameters
        const amsi = patchAmsi ? 1 : 0;
        const etw = patchEtw ? 1 : 0;
        
        // Handle the execute-assembly command
        submitCommand(String(npGuid), `execute-assembly BYPASSAMSI=${amsi} BLOCKETW=${etw} "${uploadPath}" ${assemblyArguments}`, callbackClose);
    };

    const callbackClose = () => {
        // Reset state
        setModalOpen(false);
        setAssemblyFile(null);
        setAssemblyArguments("");
        setPatchAmsi(true);
        setPatchEtw(true);
        setSubmitLoading(false);
    };

    return (
        <Modal
            opened={modalOpen}
            onClose={() => setModalOpen(false)}
            title={<b>Execute-Assembly: Execute .NET program</b>}
            size="auto"
            centered
        >
            <Text>Execute a .NET (C#) program in-memory.</Text>
            <Text>Caution: Running execute-assembly will load the CLR!</Text>

            <Space h='xl' />

            <SimpleGrid cols={1}>
            {/* File selector */}
            <FileButton onChange={setAssemblyFile}>
                {(props) => <Button color={"gray"} {...props}>
                    {assemblyFile ? "File: " + assemblyFile.name  : "Select .NET binary"}
                </Button>}
            </FileButton>
            
            {/* Arguments and options */}
            <Input 
                placeholder="Arguments"
                value={assemblyArguments}
                onChange={(event) => setAssemblyArguments(event.currentTarget.value)}
            />

            <Flex
                gap="xl"
                justify="center"
                align="center"
                >
                <Chip checked={patchAmsi} onChange={setPatchAmsi}>Patch AMSI</Chip>
                <Chip checked={patchEtw} onChange={setPatchEtw}>Block ETW</Chip>
            </Flex>

            </SimpleGrid>

            <Space h='xl' />

            {/* Submit button */}
            <Button 
                onClick={submit}
                leftIcon={<FaTerminal />}
                sx={{width: '100%'}}
                loading={submitLoading}
            >
                Execute
            </Button>
        </Modal>
    )
}

export default ExecuteAssemblyModal