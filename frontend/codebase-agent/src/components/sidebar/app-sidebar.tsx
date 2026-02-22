import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarMenuButton,
    SidebarMenuItem,
    SidebarRail,
    SidebarTrigger,
    useSidebar,
} from "@/components/ui/sidebar";
import { SquarePen } from "lucide-react";
import { AppSidebarTitle } from "./app-sidebar-title";
import { Chats } from "./chats";

export function AppSidebar() {
    const { open } = useSidebar();

    return (
        <Sidebar collapsible="icon">
            <SidebarHeader>
                <AppSidebarTitle />
            </SidebarHeader>
            <SidebarContent>
                <SidebarGroup className="gap-4">
                    <SidebarMenuItem>
                        <SidebarMenuButton>
                            <SquarePen />
                            <span>New chat</span>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                </SidebarGroup>

                {open && (
                    <>
                        <SidebarGroupLabel>Chats</SidebarGroupLabel>
                        <SidebarGroup>
                            <Chats />
                        </SidebarGroup>
                    </>
                )}
            </SidebarContent>
            <SidebarFooter>
                <SidebarTrigger />
            </SidebarFooter>
            <SidebarRail />
        </Sidebar>
    );
}
