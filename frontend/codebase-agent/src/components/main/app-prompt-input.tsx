"use client";

import { Button } from "@/components/ui/button";
import {
    PromptInput,
    PromptInputAction,
    PromptInputActions,
    PromptInputTextarea,
} from "@/components/ui/prompt-input";
import { ArrowUp, Square } from "lucide-react";
import { type Dispatch, type SetStateAction } from "react";

interface Props {
    input: string;
    setInput: Dispatch<SetStateAction<string>>;
    isLoading: boolean;
    handleSubmit: () => void;
}

export function AppPromptInput({
    input,
    setInput,
    isLoading,
    handleSubmit,
}: Props) {
    const handleValueChange = (value: string) => {
        setInput(value);
    };

    return (
        <PromptInput
            value={input}
            onValueChange={handleValueChange}
            isLoading={isLoading}
            onSubmit={handleSubmit}
            className="w-full max-w-(--breakpoint-md) mx-auto mb-2"
        >
            <PromptInputTextarea placeholder="Ask me anything..." />
            <PromptInputActions className="justify-end pt-2">
                <PromptInputAction
                    tooltip={isLoading ? "Stop generation" : "Send message"}
                >
                    <Button
                        variant="default"
                        size="icon"
                        className="h-8 w-8 rounded-full"
                        onClick={handleSubmit}
                    >
                        {isLoading ? (
                            <Square className="size-5 fill-current" />
                        ) : (
                            <ArrowUp className="size-5" />
                        )}
                    </Button>
                </PromptInputAction>
            </PromptInputActions>
        </PromptInput>
    );
}
