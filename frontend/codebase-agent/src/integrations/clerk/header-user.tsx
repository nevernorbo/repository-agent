import { Button } from "@/components/ui/button";
import {
    SignedIn,
    SignInButton,
    SignedOut,
    UserButton,
} from "@clerk/clerk-react";
import { LogIn } from "lucide-react";

export default function HeaderUser() {
    return (
        <>
            <SignedIn>
                <UserButton />
            </SignedIn>
            <SignedOut>
                <SignInButton>
                    <Button>
                        <LogIn />
                        Sign in
                    </Button>
                </SignInButton>
            </SignedOut>
        </>
    );
}
