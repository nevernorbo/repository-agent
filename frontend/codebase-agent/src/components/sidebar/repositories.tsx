import { Link } from "@tanstack/react-router";
import { Loader2 } from "lucide-react";
import { useEffect, useState } from "react";
import { SidebarMenu, SidebarMenuButton, SidebarMenuItem } from "../ui/sidebar";

interface Props {
    refreshSidebar: number;
}

export function Repositories({ refreshSidebar }: Props) {
    const [repos, setRepos] = useState<string[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        async function getRepos() {
            try {
                setLoading(true);
                const response = await fetch(
                    "http://localhost:8000/api/repositories"
                );
                if (!response.ok)
                    throw new Error("Failed to fetch repositories");

                const data = await response.json();

                setRepos(data);
            } catch (err) {
                console.error(err);
            } finally {
                setLoading(false);
            }
        }

        getRepos();
    }, [refreshSidebar]);

    if (loading) {
        return (
            <div className="flex items-center gap-2 p-4 text-sm text-muted-foreground">
                <Loader2 className="size-4 animate-spin" />
                <span>Loading repositories...</span>
            </div>
        );
    }

    return (
        <SidebarMenu>
            {repos.length === 0 ? (
                <div className="p-4 text-xs text-muted-foreground italic">
                    No repositories indexed yet.
                </div>
            ) : (
                repos.map((repo) => (
                    <SidebarMenuItem key={repo}>
                        <SidebarMenuButton asChild>
                            <Link
                                to="/repository/$id"
                                params={{ id: encodeURIComponent(repo) }}
                            >
                                <span>{repo}</span>
                            </Link>
                        </SidebarMenuButton>
                    </SidebarMenuItem>
                ))
            )}
        </SidebarMenu>
    );
}
