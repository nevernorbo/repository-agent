import { Button } from "@/components/ui/button";
import {
    Dialog,
    DialogContent,
    DialogHeader,
    DialogTitle,
    DialogTrigger,
} from "@/components/ui/dialog";
import { Input } from "@/components/ui/input";
import { ScrollArea } from "@/components/ui/scroll-area";
import {
    SidebarGroup,
    SidebarMenuButton,
    SidebarMenuItem,
} from "@/components/ui/sidebar";
import { BookPlus, Github, Loader2, Search, Star } from "lucide-react";
import { useState, type Dispatch, type SetStateAction } from "react";
import { toast } from "sonner";

interface GithubRepo {
    id: number;
    full_name: string;
    name: string;
    stargazers_count: number;
}

interface Props {
    isIndexing: boolean;
    setIsIndexing: Dispatch<SetStateAction<boolean>>;
    refreshSidebar: () => void;
}

export function IndexRepository({ isIndexing, setIsIndexing, refreshSidebar }: Props) {
    const [open, setOpen] = useState(false);
    const [username, setUsername] = useState("");
    const [repos, setRepos] = useState<GithubRepo[]>([]);
    const [loading, setLoading] = useState(false);

    const fetchRepos = async () => {
        if (!username) return;
        setLoading(true);
        try {
            const response = await fetch(
                `https://api.github.com/users/${username}/repos?sort=updated`
            );
            if (response.ok) {
                const data: GithubRepo[] = await response.json();
                setRepos(
                    data.sort(
                        (r1, r2) => r2.stargazers_count - r1.stargazers_count
                    )
                );
            } else {
                setRepos([]);
            }
        } catch (error) {
            console.error("Error fetching repos:", error);
        } finally {
            setLoading(false);
        }
    };

    const handleSelect = async (fullName: string) => {
        setIsIndexing(true);

        try {
            setOpen(false); // Close the dialog

            const response = await fetch("http://localhost:8000/api/index", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({ repo_name: fullName }),
            });

            if (!response.ok) throw new Error("Failed to trigger indexing");

            toast.success("Indexing...");

            const data = await response.json();

            if (response.ok) {
                toast.success("Cloned", {
                    description: data.message,
                });
                startPolling(fullName);
            }
        } catch (error) {
            toast.error("Error", {
                description: "Could not start the indexing process.",
            });
        }
    };

    const startPolling = (repoName: string) => {
        const interval = setInterval(async () => {
            try {
                // Encode the name because it contains a slash
                const res = await fetch(
                    `http://localhost:8000/api/index/status/${encodeURIComponent(repoName)}`
                );
                const data = await res.json();

                if (data.status === "completed") {
                    clearInterval(interval);
                    toast.success("Success!", {
                        description: `${repoName} is now indexed.`,
                    });
                    setIsIndexing(false);
                    refreshSidebar();
                } else if (data.status.startsWith("failed")) {
                    clearInterval(interval);
                    toast.error("Indexing failed", {
                        description: data.status,
                    });
                }
            } catch (e) {
                console.error("Polling error", e);
            }
        }, 1000);
    };

    return (
        <SidebarGroup className="gap-4">
            <SidebarMenuItem>
                <Dialog open={open} onOpenChange={setOpen}>
                    <DialogTrigger asChild>
                        <SidebarMenuButton>
                            <BookPlus />
                            <span>Add repository</span>
                        </SidebarMenuButton>
                    </DialogTrigger>
                    <DialogContent className="sm:max-w-[500px]">
                        <DialogHeader>
                            <DialogTitle>Add GitHub Repository</DialogTitle>
                        </DialogHeader>
                        <div className="flex gap-2 py-4">
                            <Input
                                placeholder="GitHub username (e.g. facebook)"
                                value={username}
                                onChange={(e) => setUsername(e.target.value)}
                                onKeyDown={(e) =>
                                    e.key === "Enter" && fetchRepos()
                                }
                            />
                            <Button
                                size="icon"
                                onClick={fetchRepos}
                                disabled={loading}
                            >
                                {loading ? (
                                    <Loader2 className="h-4 w-4 animate-spin" />
                                ) : (
                                    <Search className="h-4 w-4" />
                                )}
                            </Button>
                        </div>

                        <ScrollArea className="h-[300px] pr-4">
                            {repos.length > 0 ? (
                                <div className="space-y-2">
                                    {repos.map((repo) => (
                                        <button
                                            key={repo.id}
                                            onClick={() =>
                                                handleSelect(repo.full_name)
                                            }
                                            className="flex w-full items-center gap-2 rounded-lg border p-3 text-left text-sm transition-hover hover:bg-accent"
                                        >
                                            <div className="flex-1 overflow-hidden">
                                                <p className="font-medium truncate">
                                                    {repo.name}
                                                </p>
                                                <p className="flex gap-1 items-center text-xs text-muted-foreground">
                                                    <Star size={10} />{" "}
                                                    {repo.stargazers_count}
                                                </p>
                                            </div>
                                        </button>
                                    ))}
                                </div>
                            ) : (
                                <div className="flex h-full flex-col items-center justify-center text-center opacity-50">
                                    <Github className="mb-2 h-8 w-8" />
                                    <p className="text-sm">
                                        Search for a user to see their
                                        repositories
                                    </p>
                                </div>
                            )}
                        </ScrollArea>
                    </DialogContent>
                </Dialog>
            </SidebarMenuItem>
        </SidebarGroup>
    );
}
