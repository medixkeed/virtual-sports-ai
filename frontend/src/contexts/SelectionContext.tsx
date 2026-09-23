import {
  createContext,
  useCallback,
  useContext,
  useMemo,
  useState,
  type ReactNode,
} from "react";
import type { MarketType } from "../types/api";

export interface OddsSelection {
  matchId: number;
  market: MarketType;
  outcomeKey: string;
  label: string;
  odds: number;
  homeTeam: string;
  awayTeam: string;
}

interface SelectionContextValue {
  selections: OddsSelection[];
  toggleSelection: (sel: OddsSelection) => void;
  clearSelections: () => void;
  isSelected: (matchId: number, outcomeKey: string) => boolean;
}

const SelectionContext = createContext<SelectionContextValue | null>(null);

const STORAGE_KEY = "vsa_selections";

function load(): OddsSelection[] {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    return raw ? (JSON.parse(raw) as OddsSelection[]) : [];
  } catch {
    return [];
  }
}

export function SelectionProvider({ children }: { children: ReactNode }) {
  const [selections, setSelections] = useState<OddsSelection[]>(load);

  const persist = useCallback((next: OddsSelection[]) => {
    setSelections(next);
    localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
  }, []);

  const toggleSelection = useCallback(
    (sel: OddsSelection) => {
      setSelections((prev) => {
        const idx = prev.findIndex(
          (s) => s.matchId === sel.matchId && s.outcomeKey === sel.outcomeKey,
        );
        let next: OddsSelection[];
        if (idx >= 0) {
          next = prev.filter((_, i) => i !== idx);
        } else {
          const withoutSameMatch = prev.filter((s) => s.matchId !== sel.matchId);
          next = [...withoutSameMatch, sel];
        }
        localStorage.setItem(STORAGE_KEY, JSON.stringify(next));
        return next;
      });
    },
    [],
  );

  const clearSelections = useCallback(() => {
    persist([]);
  }, [persist]);

  const isSelected = useCallback(
    (matchId: number, outcomeKey: string) =>
      selections.some(
        (s) => s.matchId === matchId && s.outcomeKey === outcomeKey,
      ),
    [selections],
  );

  const value = useMemo(
    () => ({
      selections,
      toggleSelection,
      clearSelections,
      isSelected,
    }),
    [selections, toggleSelection, clearSelections, isSelected],
  );

  return (
    <SelectionContext.Provider value={value}>
      {children}
    </SelectionContext.Provider>
  );
}

export function useSelections() {
  const ctx = useContext(SelectionContext);
  if (!ctx) throw new Error("useSelections must be used within SelectionProvider");
  return ctx;
}
