import React from 'react';
import { cn } from '@/lib/utils';

interface CardProps extends React.HTMLAttributes<HTMLDivElement> {
    variant?: 'default' | 'glass' | 'bordered';
}

export const Card = React.forwardRef<HTMLDivElement, CardProps>(
    ({ className, variant = 'glass', children, ...props }, ref) => {
        const variants = {
            default: "bg-[#1A1A1A] border border-white/10",
            glass: "bg-white/5 backdrop-blur-md border border-white/10",
            bordered: "bg-transparent border border-white/20"
        };

        return (
            <div
                ref={ref}
                className={cn("rounded-2xl p-6", variants[variant], className)}
                {...props}
            >
                {children}
            </div>
        );
    }
);

Card.displayName = "Card";
