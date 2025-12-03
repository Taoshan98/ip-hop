import {
    Dialog,
    DialogContent,
    DialogDescription,
    DialogHeader,
    DialogTitle,
} from "@/components/ui/dialog";
import {
    Table,
    TableBody,
    TableCell,
    TableHead,
    TableHeader,
    TableRow,
} from "@/components/ui/table";
import { useQuery } from "@tanstack/react-query";
import api from "@/lib/api";
import { Loader2 } from "lucide-react";

interface IPHistory {
    id: number;
    ip_address: string;
    status: string;
    message: string;
    timestamp: string;
}

interface HistoryModalProps {
    domainId: number | null;
    domainName: string;
    isOpen: boolean;
    onClose: () => void;
}

// Native date formatter (replaces date-fns)
const formatTimestamp = (timestamp: string): string => {
    const date = new Date(timestamp);
    return new Intl.DateTimeFormat('en-GB', {
        year: 'numeric',
        month: '2-digit',
        day: '2-digit',
        hour: '2-digit',
        minute: '2-digit',
        second: '2-digit',
        hour12: false
    }).format(date).replace(/(\d+)\/(\d+)\/(\d+),/, '$3-$2-$1');
};

export function HistoryModal({ domainId, domainName, isOpen, onClose }: HistoryModalProps) {
    const { data: history, isLoading } = useQuery<IPHistory[]>({
        queryKey: ['history', domainId],
        queryFn: async () => {
            if (!domainId) return [];
            const res = await api.get(`/domains/${domainId}/history`);
            return res.data;
        },
        enabled: !!domainId && isOpen,
    });

    return (
        <Dialog open={isOpen} onOpenChange={onClose}>
            <DialogContent className="max-w-3xl">
                <DialogHeader>
                    <DialogTitle>IP History for {domainName}</DialogTitle>
                    <DialogDescription>
                        Recent IP update attempts and their status.
                    </DialogDescription>
                </DialogHeader>

                <div className="max-h-[60vh] overflow-auto">
                    {isLoading ? (
                        <div className="flex justify-center p-4">
                            <Loader2 className="h-6 w-6 animate-spin" />
                        </div>
                    ) : (
                        <Table>
                            <TableHeader>
                                <TableRow>
                                    <TableHead>Time</TableHead>
                                    <TableHead>IP Address</TableHead>
                                    <TableHead>Status</TableHead>
                                    <TableHead>Message</TableHead>
                                </TableRow>
                            </TableHeader>
                            <TableBody>
                                {history?.map((record) => (
                                    <TableRow key={record.id}>
                                        <TableCell className="whitespace-nowrap">
                                            {formatTimestamp(record.timestamp)}
                                        </TableCell>
                                        <TableCell className="font-mono">{record.ip_address}</TableCell>
                                        <TableCell>
                                            <span className={`px-2 py-1 rounded-full text-xs font-medium ${record.status === 'SUCCESS'
                                                ? 'bg-green-100 text-green-800'
                                                : 'bg-red-100 text-red-800'
                                                }`}>
                                                {record.status}
                                            </span>
                                        </TableCell>
                                        <TableCell className="max-w-xs truncate" title={record.message}>
                                            {record.message}
                                        </TableCell>
                                    </TableRow>
                                ))}
                                {history?.length === 0 && (
                                    <TableRow>
                                        <TableCell colSpan={4} className="text-center text-muted-foreground">
                                            No history available.
                                        </TableCell>
                                    </TableRow>
                                )}
                            </TableBody>
                        </Table>
                    )}
                </div>
            </DialogContent>
        </Dialog>
    );
}
