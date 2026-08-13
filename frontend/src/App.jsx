import React, { useState, useEffect } from 'react';

const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export default function App() {
  const [filtros, setFiltros] = useState({
    nivel_educativo: '',
    cobertura_100: false,
    q: '',
  });

  const [debouncedQ, setDebouncedQ] = useState('');
  const [becas, setBecas] = useState([]);
  const [total, setTotal] = useState(0);
  const [cargando, setCargando] = useState(false);
  const [error, setError] = useState(null);

  // Debounce de la búsqueda de texto libre.
  useEffect(() => {
    const handler = setTimeout(() => {
      setDebouncedQ(filtros.q.trim());
    }, 400);

    return () => clearTimeout(handler);
  }, [filtros.q]);

  // Consultar el backend cuando cambian los filtros.
  useEffect(() => {
    const obtenerBecas = async () => {
      setCargando(true);
      setError(null);

      try {
        const queryParams = new URLSearchParams();

        if (filtros.nivel_educativo) {
          queryParams.append(
            'nivel_educativo',
            filtros.nivel_educativo
          );
        }

        if (filtros.cobertura_100) {
          queryParams.append(
            'cobertura_100',
            'true'
          );
        }

        if (debouncedQ) {
          queryParams.append('q', debouncedQ);
        }

        const url =
          `${API_BASE_URL}/becas/?${queryParams.toString()}`;

        const res = await fetch(url);

        if (!res.ok) {
          throw new Error(
            `Error en la solicitud: ${res.status} ${res.statusText}`
          );
        }

        const data = await res.json();

        // La API devuelve PaginatedResponse:
        // { items, total, skip, limit }
        setBecas(
          Array.isArray(data.items)
            ? data.items
            : []
        );

        setTotal(
          typeof data.total === 'number'
            ? data.total
            : 0
        );
      } catch (err) {
        console.error('Error cargando becas:', err);

        setBecas([]);
        setTotal(0);

        setError(
          'No se pudieron cargar las becas en este momento. Intenta más tarde.'
        );
      } finally {
        setCargando(false);
      }
    };

    obtenerBecas();
  }, [
    filtros.nivel_educativo,
    filtros.cobertura_100,
    debouncedQ,
  ]);

  const handleChange = (e) => {
    const {
      name,
      value,
      type,
      checked,
    } = e.target;

    setFiltros((prev) => ({
      ...prev,
      [name]:
        type === 'checkbox'
          ? checked
          : value,
    }));
  };

  return (
    <div className="min-h-screen bg-slate-50 text-slate-800">
      {/* Header */}
      <header className="bg-indigo-700 text-white shadow-md">
        <div className="max-w-6xl mx-auto px-4 py-6">
          <h1 className="text-3xl font-bold tracking-tight">
            🎓 BecaRadar México
          </h1>

          <p className="mt-1 text-indigo-100">
            Buscador centralizado y actualizado de
            becas académicas en México.
          </p>
        </div>
      </header>

      {/* Main */}
      <main className="max-w-6xl mx-auto px-4 py-8">
        {/* Filtros */}
        <div className="bg-white p-6 rounded-lg shadow-sm border border-slate-200 mb-8">
          <h2 className="text-lg font-semibold mb-4 text-slate-700">
            Filtrar Becas
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 items-end">
            {/* Búsqueda */}
            <div>
              <label
                htmlFor="q"
                className="block text-sm font-medium text-slate-600 mb-1"
              >
                Búsqueda General / Institución
              </label>

              <input
                type="text"
                id="q"
                name="q"
                placeholder="Ej. UNAM, Excelencia..."
                value={filtros.q}
                onChange={handleChange}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-indigo-500"
              />
            </div>

            {/* Nivel */}
            <div>
              <label
                htmlFor="nivel_educativo"
                className="block text-sm font-medium text-slate-600 mb-1"
              >
                Nivel Educativo
              </label>

              <select
                id="nivel_educativo"
                name="nivel_educativo"
                value={filtros.nivel_educativo}
                onChange={handleChange}
                className="w-full border border-slate-300 rounded-md px-3 py-2 text-sm bg-white focus:outline-none focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">
                  Todos los niveles
                </option>

                <option value="basica">
                  Educación básica
                </option>

                <option value="preparatoria">
                  Preparatoria / Bachillerato
                </option>

                <option value="universidad">
                  Universidad / Licenciatura
                </option>

                <option value="posgrado">
                  Posgrado
                </option>

                <option value="general">
                  General
                </option>
              </select>
            </div>

            {/* Cobertura */}
            <div className="flex items-center h-10">
              <label className="flex items-center cursor-pointer select-none text-sm text-slate-700 font-medium">
                <input
                  type="checkbox"
                  name="cobertura_100"
                  checked={filtros.cobertura_100}
                  onChange={handleChange}
                  className="h-4 w-4 text-indigo-600 rounded border-slate-300 focus:ring-indigo-500 mr-2"
                />

                Solo becas de Cobertura 100%
              </label>
            </div>
          </div>
        </div>

        {/* Cargando */}
        {cargando && (
          <div className="text-center py-12">
            <p className="text-slate-500 font-medium">
              Cargando convocatorias...
            </p>
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-700 p-4 rounded-md mb-6">
            {error}
          </div>
        )}

        {/* Resultados */}
        {!cargando && !error && (
          <>
            <div className="flex justify-between items-center mb-4">
              <span className="text-sm font-medium text-slate-500">
                Se encontraron {total} becas disponibles
              </span>
            </div>

            {becas.length === 0 ? (
              <div className="bg-white p-8 text-center rounded-lg border border-slate-200">
                <p className="text-slate-500">
                  No se encontraron becas que coincidan
                  con los criterios seleccionados.
                </p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {becas.map((beca) => {
                  const institucion =
                    beca.institucion?.nombre ||
                    'Institución';

                  const tieneCobertura100 =
                    typeof beca.cobertura === 'string' &&
                    beca.cobertura
                      .toLowerCase()
                      .includes('100%');

                  return (
                    <div
                      key={beca.id}
                      className="bg-white border border-slate-200 rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200 p-5 flex flex-col justify-between"
                    >
                      <div>
                        <div className="flex justify-between items-start mb-2 gap-2">
                          <span className="text-xs font-semibold uppercase tracking-wider px-2.5 py-1 bg-indigo-50 text-indigo-700 rounded-full">
                            {institucion}
                          </span>

                          {tieneCobertura100 && (
                            <span className="text-xs font-semibold px-2 py-0.5 bg-emerald-100 text-emerald-800 rounded">
                              100% Cobertura
                            </span>
                          )}
                        </div>

                        <h3 className="text-lg font-bold text-slate-900 mt-2 mb-2 line-clamp-2">
                          {beca.nombre}
                        </h3>

                        <p className="text-sm text-slate-600 mb-3 line-clamp-3">
                          <span className="font-semibold">
                            Requisitos:{' '}
                          </span>

                          {beca.requisitos ||
                            'Consultar bases oficiales.'}
                        </p>

                        <p className="text-xs text-slate-500">
                          <span className="font-medium text-slate-700">
                            Nivel:{' '}
                          </span>

                          {beca.nivel_educativo ||
                            'No especificado'}
                        </p>

                        {beca.ubicacion && (
                          <p className="text-xs text-slate-500 mt-1">
                            <span className="font-medium text-slate-700">
                              Ubicación:{' '}
                            </span>

                            {beca.ubicacion}
                          </p>
                        )}
                      </div>

                      <div className="border-t border-slate-100 pt-3 mt-4 text-xs text-slate-500 flex flex-col gap-1">
                        <div>
                          <span className="font-medium text-slate-700">
                            Cobertura:{' '}
                          </span>

                          {beca.cobertura ||
                            'No especificada'}
                        </div>

                        <div>
                          <span className="font-medium text-slate-700">
                            Fecha Límite:{' '}
                          </span>

                          {beca.fecha_limite
                            ? beca.fecha_limite
                            : 'Por confirmar / Continua'}
                        </div>

                        {beca.link_oficial && (
                          <a
                            href={beca.link_oficial}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="mt-3 block text-center bg-indigo-600 hover:bg-indigo-700 text-white font-medium py-2 px-4 rounded text-sm transition-colors"
                          >
                            Ver Convocatoria Oficial
                          </a>
                        )}
                      </div>
                    </div>
                  );
                })}
              </div>
            )}
          </>
        )}
      </main>
    </div>
  );
}