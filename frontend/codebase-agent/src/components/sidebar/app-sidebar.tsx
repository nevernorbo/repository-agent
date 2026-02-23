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
import { Loader2 } from "lucide-react";
import { useState } from "react";
import { AppSidebarTitle } from "./app-sidebar-title";
import { IndexRepository } from "./index-repository";
import { Repositories } from "./repositories";

export function AppSidebar() {
    const { open } = useSidebar();
    const [isIndexing, setIsIndexing] = useState(false);
    const [trigger, setTrigger] = useState(0);

    return (
        <Sidebar collapsible="icon">
            <SidebarHeader>
                <AppSidebarTitle />
            </SidebarHeader>
            <SidebarContent>
                <IndexRepository
                    isIndexing={isIndexing}
                    setIsIndexing={setIsIndexing}
                    refreshSidebar={() => setTrigger((prev) => prev + 1)}
                />
                {open && (
                    <>
                        {isIndexing && (
                            <>
                                <div className="flex items-center gap-2 p-4 text-sm text-muted-foreground">
                                    <Loader2 className="size-4 animate-spin" />
                                    <span>Indexing in progress...</span>
                                </div>
                            </>
                        )}
                        <SidebarGroupLabel>Repositories</SidebarGroupLabel>
                        <SidebarGroup>
                            <Repositories refreshSidebar={trigger} />
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
