import { HeadContent, Scripts, createRootRoute } from "@tanstack/react-router";

import ClerkProvider from "../integrations/clerk/provider";

import appCss from "../styles.css?url";
import { AppMain } from "@/components/main/app-main";
import { AppSidebar } from "@/components/sidebar/app-sidebar";
import { SidebarProvider } from "@/components/ui/sidebar";

export const Route = createRootRoute({
    head: () => ({
        meta: [
            {
                charSet: "utf-8",
            },
            {
                name: "viewport",
                content: "width=device-width, initial-scale=1",
            },
            {
                title: "Codebase agent",
            },
        ],
        links: [
            {
                rel: "stylesheet",
                href: appCss,
            },
        ],
    }),
    shellComponent: RootDocument,
});

function RootDocument({ children }: { children: React.ReactNode }) {
    return (
        <html lang="en">
            <head>
                <HeadContent />
            </head>
            <body>
                <ClerkProvider>
                    <SidebarProvider>
                        <AppSidebar />
                        <AppMain>{children}</AppMain>
                    </SidebarProvider>
                </ClerkProvider>
                <Scripts />
            </body>
        </html>
    );
}
