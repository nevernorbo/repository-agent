import { SquarePen } from "lucide-react";
import { Button } from "../ui/button";

export function NewChat({ open }: { open: boolean }) {
    return (
        <Button>
            <SquarePen />
            {open && <span>New Chat</span>}
        </Button>
    );
}
