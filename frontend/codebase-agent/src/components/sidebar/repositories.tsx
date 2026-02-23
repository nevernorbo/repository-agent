import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "../ui/sidebar";

export function Repositories() {
    const repositories = [
        {
            name: "Chat 1",
            id: "some id",
        },
        {
            name: "Chat 2",
            id: "some id",
        },
        {
            name: "Chat 3",
            id: "some id",
        },
        {
            name: "Chat 4",
            id: "some id",
        },
    ];

    return (
        <SidebarMenu>
            {repositories.map((repository) => (
                <SidebarMenuItem key={repository.name}>
                    <SidebarMenuButton asChild>
                        <a href={`repository/${repository.id}`}>
                            <span>{repository.name}</span>
                        </a>
                    </SidebarMenuButton>
                </SidebarMenuItem>
            ))}
        </SidebarMenu>
    );
}
