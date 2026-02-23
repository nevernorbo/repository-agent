import {
    Sidebar,
    SidebarContent,
    SidebarFooter,
    SidebarGroup,
    SidebarGroupLabel,
    SidebarHeader,
    SidebarRail,
    SidebarTrigger,
    useSidebar,
} from "@/components/ui/sidebar";
import { AppSidebarTitle } from "./app-sidebar-title";
import { Repositories } from "./repositories";
import { IndexRepository } from "./index-repository";

export function AppSidebar() {
    const { open } = useSidebar();

    return (
        <Sidebar collapsible="icon">
            <SidebarHeader>
                <AppSidebarTitle />
            </SidebarHeader>
            <SidebarContent>
                <IndexRepository />
                {open && (
                    <>
                        <SidebarGroupLabel>Repositories</SidebarGroupLabel>
                        <SidebarGroup>
                            <Repositories />
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
