export interface Torrent {
    name: string;
    info_hash: string;
    description: string; 
    category: string[]; 
    magnet_link: string;
}
