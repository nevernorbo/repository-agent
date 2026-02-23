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
}

export function Chat({ repository }: Props) {
    const [messages, setMessages] = useState<IMessage[]>([]);
    const [isLoading, setIsLoading] = useState(false);
    const [input, setInput] = useState("");

    const handleSubmit = () => {
        const message = input;
        if (!message.trim()) return;

        setIsLoading(true);
        setInput("");

        const newMessage = {
            id: messages[messages.length - 1]?.id + 1,
            content: message,
            role: "user",
        } as IMessage;

        setMessages((prev) => [...prev, newMessage]);

        setTimeout(() => {
            setIsLoading(false);
        }, 5000);
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
