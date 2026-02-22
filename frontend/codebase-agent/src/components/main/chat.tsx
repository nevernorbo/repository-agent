"use client";

import {
    ChatContainerContent,
    ChatContainerRoot,
} from "@/components/ui/chat-container";
import { Markdown } from "@/components/ui/markdown";
import {
    Message,
    MessageAvatar,
    MessageContent,
} from "@/components/ui/message";
import { useState } from "react";

export function Chat() {
    const [messages, setMessages] = useState([
        {
            id: 1,
            role: "user",
            content: "Hello! Can you help me with a coding question?",
        },
        {
            id: 2,
            role: "assistant",
            content:
                "Of course! I'd be happy to help with your coding question. What would you like to know?",
        },
        {
            id: 3,
            role: "user",
            content: "How do I create a responsive layout with CSS Grid?",
        },
        {
            id: 4,
            role: "assistant",
            content:
                "Creating a responsive layout with CSS Grid is straightforward. Here's a basic example:\n\n```css\n.container {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n  gap: 1rem;\n}\n```\n\nThis creates a grid where:\n- Columns automatically fit as many as possible\n- Each column is at least 250px wide\n- Columns expand to fill available space\n- There's a 1rem gap between items\n\nWould you like me to explain more about how this works?",
        },
        {
            id: 5,
            role: "assistant",
            content:
                "Of course! I'd be happy to help with your coding question. What would you like to know?",
        },
        {
            id: 6,
            role: "user",
            content: "How do I create a responsive layout with CSS Grid?",
        },
        {
            id: 7,
            role: "assistant",
            content:
                "Creating a responsive layout with CSS Grid is straightforward. Here's a basic example:\n\n```css\n.container {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n  gap: 1rem;\n}\n```\n\nThis creates a grid where:\n- Columns automatically fit as many as possible\n- Each column is at least 250px wide\n- Columns expand to fill available space\n- There's a 1rem gap between items\n\nWould you like me to explain more about how this works?",
        },
        {
            id: 8,
            role: "user",
            content: "How do I create a responsive layout with CSS Grid?",
        },
        {
            id: 9,
            role: "assistant",
            content:
                "Creating a responsive layout with CSS Grid is straightforward. Here's a basic example:\n\n```css\n.container {\n  display: grid;\n  grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));\n  gap: 1rem;\n}\n```\n\nThis creates a grid where:\n- Columns automatically fit as many as possible\n- Each column is at least 250px wide\n- Columns expand to fill available space\n- There's a 1rem gap between items\n\nWould you like me to explain more about how this works?",
        },
        {
            id: 10,
            role: "user",
            content: "How do I create a responsive layout with CSS Grid?",
        },
    ]);

    return (
        <div className="flex w-full flex-col overflow-hidden">
            <ChatContainerRoot className="flex-1">
                <ChatContainerContent className="space-y-4 p-4 mx-auto max-w-(--breakpoint-md)">
                    {messages.map((message) => {
                        const isAssistant = message.role === "assistant";

                        return (
                            <Message
                                key={message.id}
                                className={
                                    message.role === "user"
                                        ? "justify-end"
                                        : "justify-start"
                                }
                            >
                                {isAssistant && (
                                    <MessageAvatar
                                        src="/avatars/ai.png"
                                        alt="AI Assistant"
                                        fallback="AI"
                                    />
                                )}
                                <div className="max-w-[85%] flex-1 sm:max-w-[75%]">
                                    {isAssistant ? (
                                        <div className="bg-secondary text-foreground prose rounded-lg p-2">
                                            <Markdown>
                                                {message.content}
                                            </Markdown>
                                        </div>
                                    ) : (
                                        <MessageContent className="bg-primary text-primary-foreground">
                                            {message.content}
                                        </MessageContent>
                                    )}
                                </div>
                            </Message>
                        );
                    })}
                </ChatContainerContent>
            </ChatContainerRoot>
        </div>
    );
}
