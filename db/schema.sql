-- 1. TABLES
-- Profiles table: Stores application-specific data for each user
CREATE TABLE public.profiles (
  id uuid REFERENCES auth.users ON DELETE CASCADE PRIMARY KEY,
  username text UNIQUE NOT NULL,
  role text DEFAULT 'player' CHECK (role IN ('admin', 'player')),
  is_approved boolean DEFAULT false,
  telegram_id bigint UNIQUE,
  link_code text UNIQUE,
  -- Using 'GMT' timezone explicitly
  created_at timestamp with time zone DEFAULT (now() AT TIME ZONE 'GMT')
);

-- Invitation Tokens table
CREATE TABLE public.invitation_tokens (
  id uuid DEFAULT gen_random_uuid() PRIMARY KEY,
  token text UNIQUE NOT NULL,
  is_used boolean DEFAULT false,
  created_at timestamp with time zone DEFAULT (now() AT TIME ZONE 'GMT')
);

-- 2. AUTOMATION (TRIGGERS)
-- This function runs every time a new user confirms their email/signup
CREATE OR REPLACE FUNCTION public.handle_new_user()
RETURNS trigger AS $$
BEGIN
  INSERT INTO public.profiles (id, username, is_approved)
  VALUES (
    new.id, 
    COALESCE(new.raw_user_meta_data->>'username', 'Explorer_' || substring(new.id::text from 1 for 5)),
    false -- All new users must be approved via the invitation token logic in the app
  );
  RETURN new;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Trigger execution
CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE PROCEDURE public.handle_new_user();

-- 3. SECURITY (RLS)
ALTER TABLE public.profiles ENABLE ROW LEVEL SECURITY;
ALTER TABLE public.invitation_tokens ENABLE ROW LEVEL SECURITY;

-- Policies
CREATE POLICY "Users can view own profile" 
ON public.profiles FOR SELECT 
USING (auth.uid() = id);

CREATE POLICY "Admins can view everything" 
ON public.profiles FOR ALL 
USING (
  EXISTS (
    SELECT 1 FROM public.profiles 
    WHERE id = auth.uid() AND role = 'admin'
  )
);
