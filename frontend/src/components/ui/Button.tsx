import React from 'react';
import { cn } from '@/lib/utils';

interface ButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
    variant?: 'primary' | 'secondary' | 'ghost' | 'danger';
    size?: 'sm' | 'md' | 'lg';
    isLoading?: boolean;
}

export const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
    ({ className, variant = 'primary', size = 'md', isLoading, children, ...props }, ref) => {
        const baseStyles = "inline-flex items-center justify-center rounded-lg font-medium transition-all duration-200 focus:outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed";

        const variants = {
            primary: "bg-[rgb(var(--sage-accent))] text-black hover:bg-[rgb(var(--sage-accent))]/90 focus:ring-[rgb(var(--sage-accent))]",
            secondary: "bg-white/10 text-white hover:bg-white/20 focus:ring-white/20",
            ghost: "bg-transparent text-gray-300 hover:text-white hover:bg-white/5",
            danger: "bg-red-500/20 text-red-400 border border-red-500/50 hover:bg-red-500/30"
        };

        const sizes = {
            sm: "px-3 py-1.5 text-sm",
            md: "px-4 py-2 text-base",
            lg: "px-6 py-3 text-lg"
        };

        return (
            <button
                ref={ref}
                className={cn(baseStyles, variants[variant], sizes[size], className)}
                disabled={isLoading || props.disabled}
                {...props}
            >
                {isLoading ? (
                    <span className="mr-2 animate-spin">⏳</span>
                ) : null}
                {children}
            </button>
        );
    }
);

Button.displayName = "Button";
