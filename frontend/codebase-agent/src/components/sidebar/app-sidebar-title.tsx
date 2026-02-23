import { Bot } from "lucide-react";
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "../ui/sidebar";
import { Link } from "@tanstack/react-router";

export function AppSidebarTitle() {
    return (
        <SidebarMenu>
            <SidebarMenuItem>
                <SidebarMenuButton size="lg" asChild>
                    <Link to="/">
                        <div className="bg-sidebar-primary text-sidebar-primary-foreground flex aspect-square size-8 items-center justify-center rounded-lg">
                            <Bot className="size-4" />
                        </div>
                        <div className="flex flex-col gap-0.5 leading-none">
                            <span className="font-medium text-nowrap">
                                Codebase agent
                            </span>
                        </div>
                    </Link>
                </SidebarMenuButton>
            </SidebarMenuItem>
        </SidebarMenu>
    );
}
