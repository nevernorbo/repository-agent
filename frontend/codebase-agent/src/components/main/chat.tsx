"use client";

import { useState } from "react";
import { AppPromptInput } from "./app-prompt-input";
import { Messages } from "./messages";

export interface IMessage {
    id: number;
    role: "assistant" | "user";
    content: string;
}

interface Props {
    repository: string;
    userId: string;
    sessionId: string;
}

export function Chat({ repository, userId, sessionId }: Props) {
    const [messages, setMessages] = useState<IMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [input, setInput] = useState("");

    const handleSubmit = async () => {
        const messageText = input.trim();
        if (!messageText || isLoading) return;

        const newMessageId = !!messages.length ? messages[messages.length].id + 1 : 0;
        // Optimistic UI update: show the user's message immediately
        const newUserMessage: IMessage = {
            id: newMessageId,
            content: messageText,
            role: "user",
        };

        setMessages((prev) => [...prev, newUserMessage]);
        setInput("");
        setIsLoading(true);

        try {
            const response = await fetch("http://localhost:8100/run", {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    appName: "agent",
                    userId: userId,
                    sessionId: sessionId,
                    newMessage: {
                        role: "user",
                        parts: [
                            {
                                text: messageText,
                            },
                        ],
                    },
                    stateDelta: {
                        repository: repository,
                    },
                    streaming: false,
                }),
            });

            if (!response.ok) {
                throw new Error(
                    `ADK server responded with status: ${response.status}`
                );
            }

            // data is an array of agent interaction steps
            const data = await response.json();
            console.log("Agent run steps:", data);

            // 1. Filter and map the ADK response array into IMessage objects
            const newAgentMessages = data
                // Only keep steps that have actual text content (ignore tool/transfer steps)
                .filter((step: any) => step.content?.parts?.[0]?.text)
                .map((step: any, index: number) => {
                    const agentName = step.author || "system";
                    const textContent = step.content.parts[0].text;

                    return {
                        id: newMessageId + index + 2,
                        // Prepend the agent's name so you can see who is talking in the UI
                        content: `**[${agentName}]**\n\n${textContent}`,
                        role: "assistant",
                    } as IMessage;
                });

            // 2. Append all generated agent messages to the chat
            if (newAgentMessages.length > 0) {
                setMessages((prev) => [...prev, ...newAgentMessages]);
            } else {
                // Fallback in case the agents ran but produced no text
                setMessages((prev) => [
                    ...prev,
                    {
                        id: newMessageId + 1,
                        content: "No text response generated.",
                        role: "assistant",
                    },
                ]);
            }
        } catch (error) {
            console.error("Failed to fetch response from agent:", error);
        } finally {
            setIsLoading(false);
        }
    };

    return (
        <>
            <div className="flex-1 flex w-full flex-col min-h-0">
                <Messages messages={messages} />
            </div>
            <AppPromptInput
                handleSubmit={handleSubmit}
                input={input}
                setInput={setInput}
                isLoading={isLoading}
            />
        </>
    );
}
