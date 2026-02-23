import { BookPlus } from "lucide-react";
import {
    SidebarGroup,
    SidebarMenuButton,
    SidebarMenuItem,
} from "../ui/sidebar";

export function IndexRepository() {
    return (
        <SidebarGroup className="gap-4">
            <SidebarMenuItem>
                <SidebarMenuButton>
                    <BookPlus />
                    <span>Add repository</span>
                </SidebarMenuButton>
            </SidebarMenuItem>
        </SidebarGroup>
    );
}
