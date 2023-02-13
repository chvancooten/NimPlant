import { Button, CloseButton, FileButton, Grid, Group, Input, Modal, NativeSelect, Space, Stack, Text } from "@mantine/core"
import { Dispatch, SetStateAction, useState } from "react";
import { FaTerminal } from "react-icons/fa"
import { submitCommand } from "../../modules/nimplant";


interface IProps {
    modalOpen: boolean;
    setModalOpen: Dispatch<SetStateAction<boolean>>;
    npGuid: string | undefined;
}

interface Argument {
    value: string;
    type: string;
}

function InlineExecuteModal({ modalOpen, setModalOpen, npGuid }: IProps) {
    const [bofFile, setBofFile] = useState<File | null>(null);
    const [bofEntryPoint, setBofEntryPoint] = useState("go");
    const [bofArgs, setBofArgs] = useState<Argument[]>([]);
    const [submitLoading, setSubmitLoading] = useState(false);

    const addArgument = () => {
        setBofArgs([...bofArgs, { value: "", type: "z" }]);
    };

    const updateArgument = (index: number, value: string, type: string) => {
        setBofArgs(bofArgs.map((arg, i) => (i === index ? { value, type } : arg)));
    };

    const removeArgument = (index: number) => {
        setBofArgs(bofArgs.filter((_, i) => i !== index));
    };

    const submit = () => {
        // Read the BOF file to base64
        const reader = new FileReader();
        reader.readAsDataURL(bofFile as File);
        reader.onload = (e) => {
            const bofData = e.target?.result as string;
            const b64Bof = bofData.replace('data:', '').replace(/^.+,/, '');

            // Parse the arguments into a string
            const bofArgString: string = bofArgs.map((arg) => {
                return `${arg.value} ${arg.type}`;
            }).join(' ');
    
            // Submit the command
            setSubmitLoading(true);
            submitCommand(String(npGuid), `inline-execute ${b64Bof} ${bofEntryPoint} ${bofArgString}`, callbackClose);
        };

        const callbackClose = () => {
            // Reset state
            setModalOpen(false);
            setBofFile(null);
            setBofEntryPoint("go");
            setBofArgs([]);
            setSubmitLoading(false);
        };
    };

    return (
        <Modal
            opened={modalOpen}
            onClose={() => setModalOpen(false)}
            title={<b>Inline-Execute: Execute BOF file</b>}
            size="auto"
            centered
        >
            <Text>Execute a Beacon Object File (BOF) in-memory.</Text>
            <Text>Caution: BOF crashes will crash NimPlant too!</Text>

            <Space h='xl' />

            {/* File selector */}
            <Grid columns={4}>
                <Grid.Col span={3}>
                    <Group grow>
                        <FileButton onChange={setBofFile}>
                            {(props) => <Button color={"gray"} {...props}>
                                {bofFile ? "BOF file: " + bofFile.name  : "Select x64 BOF file"}
                            </Button>}
                        </FileButton>
                    </Group>
                </Grid.Col>
            
            {/* Entrypoint */}
                <Grid.Col span={1}>
                    <Input 
                    placeholder="Entrypoint"
                    value={bofEntryPoint}
                    onChange={(event) => setBofEntryPoint(event.currentTarget.value)}
                    />
                </Grid.Col>
            </Grid>

            {/* Dynamic argument selection */}
            <Stack py={bofArgs.length > 0 ? "lg" : "sm"}>
                {bofArgs.map((arg, index) => (
                    <Grid key={index} columns={12}>
                        <Grid.Col span={8}>
                            <Input
                            placeholder={`Argument ${index+1}`}
                            value={arg.value} 
                            onChange={(event) => updateArgument(index, event.currentTarget.value, arg.type)}
                            />
                        </Grid.Col>

                        <Grid.Col span={3}>
                            <NativeSelect
                            placeholder="Argument type" 
                            value={arg.type} 
                            onChange={(event) => updateArgument(index, arg.value, event.currentTarget.value)}
                            data={[
                                { label: 'String', value: 'z' },
                                { label: 'Wide String', value: 'Z' },
                                { label: 'Integer', value: 'i' },
                                { label: 'Short', value: 's' },
                                { label: 'Binary (b64)', value: 'b' },
                            ]} />
                        </Grid.Col>
                        
                        <Grid.Col span={1}>
                            <CloseButton size="lg" 
                            onClick={() => removeArgument(index)}
                            />
                        </Grid.Col>
                    </Grid>
                ))}
            </Stack>
            
            <Group grow>
                <Button color="gray" onClick={addArgument}>Add argument</Button>
            </Group>

            <Space h='xl' />

            {/* Submit button */}
            <Button 
                onClick={submit}
                leftIcon={<FaTerminal />}
                loading={submitLoading}
                sx={{width: '100%'}}
            >
                Execute
            </Button>
        </Modal>
    )
}

export default InlineExecuteModal