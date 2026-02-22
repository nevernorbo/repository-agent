import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "../ui/sidebar";

export function Chats() {
    const chats = [
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
            {chats.map((chat) => (
                <SidebarMenuItem key={chat.name}>
                    <SidebarMenuButton asChild>
                        <a href={`chats/${chat.id}`}>
                            <span>{chat.name}</span>
                        </a>
                    </SidebarMenuButton>
                </SidebarMenuItem>
            ))}
        </SidebarMenu>
    );
}
