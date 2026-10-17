import { CircleMarker, MapContainer, Popup, TileLayer } from "react-leaflet";

import { usePropertyMap } from "@/hooks/useProperties";
import { flagShort, money } from "@/lib/format";
import { useFilterStore } from "@/store/filters";

const COLOR: Record<string, string> = {
  g: "var(--green)",
  a: "var(--amber)",
  r: "var(--red)",
};

// Centro aproximado de New Jersey.
const NJ_CENTER: [number, number] = [40.2, -74.5];

export default function PropertyMap({ onOpen }: { onOpen: (id: string) => void }) {
  const flag = useFilterStore((s) => s.flag);
  const county = useFilterStore((s) => s.county_id);
  const { data } = usePropertyMap(flag, county);
  const features = data ?? [];

  return (
    <div className="card-surface overflow-hidden" style={{ height: "70vh" }}>
      <MapContainer center={NJ_CENTER} zoom={8} style={{ height: "100%", width: "100%" }}>
        <TileLayer
          attribution='&copy; OpenStreetMap'
          url="https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png"
        />
        {features.map((f) => {
          const s = flagShort(f.flag);
          return (
            <CircleMarker
              key={f.id}
              center={[f.lat, f.lng]}
              radius={9}
              pathOptions={{ color: COLOR[s], fillColor: COLOR[s], fillOpacity: 0.85, weight: 2 }}
              eventHandlers={{ click: () => onOpen(f.id) }}
            >
              <Popup>{money(f.opening_price)}</Popup>
            </CircleMarker>
          );
        })}
      </MapContainer>
    </div>
  );
}
