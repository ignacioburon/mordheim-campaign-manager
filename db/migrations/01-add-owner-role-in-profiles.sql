
/* ESTRUCTURA DE PERMISOS MORDHEIM CLUB DRAGÓN
   1. Configurar columna de roles
   2. Asignar Owner
*/

-- AÑADIR COLUMNA SI NO EXISTE (Por seguridad)
DO $$ 
BEGIN 
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='profiles' AND column_name='role') THEN
        ALTER TABLE public.profiles ADD COLUMN role TEXT DEFAULT 'player';
    END IF;
END $$;

-- PASO 1: RECONFIGURAR LA RESTRICCIÓN DE ROLES
-- Primero borramos la anterior para evitar conflictos de "Constraint ya existente"
ALTER TABLE public.profiles 
DROP CONSTRAINT IF EXISTS profiles_role_check;

-- Aplicamos la nueva lista de rangos permitidos
ALTER TABLE public.profiles 
ADD CONSTRAINT profiles_role_check 
CHECK (role IN ('player', 'admin', 'owner'));
