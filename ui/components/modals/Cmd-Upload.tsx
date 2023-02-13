import { Button, FileButton, Input, Modal, SimpleGrid, Space, Text } from "@mantine/core"
import { Dispatch, SetStateAction, useState } from "react";
import { FaUpload } from "react-icons/fa"
import { submitCommand, uploadFile } from "../../modules/nimplant";


interface IProps {
    modalOpen: boolean;
    setModalOpen: Dispatch<SetStateAction<boolean>>;
    npGuid: string | undefined;
}

function UploadModal({ modalOpen, setModalOpen, npGuid }: IProps) {
    const [file, setFile] = useState<File | null>(null);
    const [targetPath, setTargetPath] = useState("");
    const [submitLoading, setSubmitLoading] = useState(false);

    const submit = () => {
        // Check if a file is selected
        if (!file || file === null) {
            return;
        }

        // Upload the file
        setSubmitLoading(true);
        uploadFile(file, callbackCommand, callbackClose);
    };

    const callbackCommand = (uploadPath: string) => {
        // Handle the upload command
        submitCommand(String(npGuid), `upload "${uploadPath}" "${targetPath}"`, callbackClose);
    };

    const callbackClose = () => {
            // Reset state
            setModalOpen(false);
            setFile(null);
            setTargetPath("");
            setSubmitLoading(false);
        };

    return (
        <Modal
            opened={modalOpen}
            onClose={() => setModalOpen(false)}
            title={<b>Upload: Upload a file</b>}
            size="auto"
            centered
        >
            <Text>Upload a file to the target.</Text>

            <Space h='xl' />

            <SimpleGrid cols={1}>
            {/* File selector */}
            <FileButton onChange={setFile}>
                {(props) => <Button color={"gray"} {...props}>
                    {file ? "File: " + file.name  : "Select file"}
                </Button>}
            </FileButton>
            
            {/* Arguments and options */}
            <Input 
                placeholder="Destination Path (optional)"
                value={targetPath}
                onChange={(event) => setTargetPath(event.currentTarget.value)}
            />

            </SimpleGrid>

            <Space h='xl' />

            {/* Submit button */}
            <Button 
                onClick={submit}
                leftIcon={<FaUpload />}
                sx={{width: '100%'}}
                loading={submitLoading}
            >
                Upload
            </Button>
        </Modal>
    )
}

export default UploadModal