import { Button, Modal, Space } from "@mantine/core"
import { FaSkull } from "react-icons/fa"
import { serverExit } from "../../modules/nimplant";
import { Dispatch, SetStateAction } from "react";


interface IProps {
    modalOpen: boolean;
    setModalOpen: Dispatch<SetStateAction<boolean>>;
}


function ExitServerModal({ modalOpen, setModalOpen }: IProps) {
    return (
        <Modal
            opened={modalOpen}
            onClose={() => setModalOpen(false)}
            title={<b>Danger zone!</b>}
            centered
        >
            Are you sure you want to exit the server? All active nimplants will be killed.

            <Space h='xl' />

            <Button 
                onClick={() => {setModalOpen(false); serverExit()}}
                leftIcon={<FaSkull />} sx={{width: '100%'}}
            >
                Yes, kill kill kill!
            </Button>
        </Modal>
    )
}

export default ExitServerModal