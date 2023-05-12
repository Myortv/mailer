--
-- PostgreSQL database dump
--

-- Dumped from database version 15.2
-- Dumped by pg_dump version 15.2

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: phonecode; Type: DOMAIN; Schema: public; Owner: postgres
--

CREATE DOMAIN public.phonecode AS character varying(3)
	CONSTRAINT phonecode_check CHECK (((VALUE)::text ~ '^[0-9]{3}$'::text));


ALTER DOMAIN public.phonecode OWNER TO postgres;

--
-- Name: phonenumber; Type: DOMAIN; Schema: public; Owner: postgres
--

CREATE DOMAIN public.phonenumber AS character varying(11)
	CONSTRAINT phonenumber_check CHECK (((VALUE)::text ~ '^7[0-9]{10}$'::text));


ALTER DOMAIN public.phonenumber OWNER TO postgres;

SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: client; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.client (
    id integer NOT NULL,
    mobile_operator_code public.phonecode NOT NULL,
    tag text,
    timezone text,
    start_recieve time without time zone,
    recieve_duration interval,
    phone_number public.phonenumber NOT NULL
);


ALTER TABLE public.client OWNER TO postgres;

--
-- Name: available_clients; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.available_clients AS
 SELECT client.id,
    client.mobile_operator_code,
    client.tag,
    client.timezone,
    client.start_recieve,
    client.recieve_duration,
    client.phone_number
   FROM public.client
  WHERE (((now() AT TIME ZONE client.timezone) >= (((now() AT TIME ZONE client.timezone))::date + client.start_recieve)) AND ((now() AT TIME ZONE client.timezone) <= ((((now() AT TIME ZONE client.timezone))::date + client.start_recieve) + client.recieve_duration)));


ALTER TABLE public.available_clients OWNER TO postgres;

--
-- Name: mailing; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.mailing (
    id integer NOT NULL,
    start_time timestamp with time zone DEFAULT now(),
    end_time timestamp with time zone,
    body text NOT NULL,
    filters json DEFAULT '{}'::json
);


ALTER TABLE public.mailing OWNER TO postgres;

--
-- Name: available_mailings; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.available_mailings AS
 SELECT mailing.id,
    mailing.start_time,
    mailing.end_time,
    mailing.body,
    mailing.filters
   FROM public.mailing
  WHERE ((now() >= mailing.start_time) AND (now() <= mailing.end_time));


ALTER TABLE public.available_mailings OWNER TO postgres;

--
-- Name: client_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.client_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.client_id_seq OWNER TO postgres;

--
-- Name: client_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.client_id_seq OWNED BY public.client.id;


--
-- Name: mailing_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.mailing_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.mailing_id_seq OWNER TO postgres;

--
-- Name: mailing_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.mailing_id_seq OWNED BY public.mailing.id;


--
-- Name: message; Type: TABLE; Schema: public; Owner: postgres
--

CREATE TABLE public.message (
    id integer NOT NULL,
    time_created timestamp with time zone DEFAULT now(),
    status text DEFAULT 'awaits'::text,
    mailing_id integer,
    client_id integer
);


ALTER TABLE public.message OWNER TO postgres;

--
-- Name: message_id_seq; Type: SEQUENCE; Schema: public; Owner: postgres
--

CREATE SEQUENCE public.message_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER TABLE public.message_id_seq OWNER TO postgres;

--
-- Name: message_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: postgres
--

ALTER SEQUENCE public.message_id_seq OWNED BY public.message.id;


--
-- Name: message_status_stats; Type: VIEW; Schema: public; Owner: postgres
--

CREATE VIEW public.message_status_stats AS
 SELECT jsoned.mailing_id,
    json_agg(json_build_object(jsoned.status, jsoned.count)) AS status
   FROM ( SELECT count(message.id) AS count,
            message.mailing_id,
            message.status
           FROM public.message
          GROUP BY message.status, message.mailing_id) jsoned
  GROUP BY jsoned.mailing_id;


ALTER TABLE public.message_status_stats OWNER TO postgres;

--
-- Name: client id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client ALTER COLUMN id SET DEFAULT nextval('public.client_id_seq'::regclass);


--
-- Name: mailing id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mailing ALTER COLUMN id SET DEFAULT nextval('public.mailing_id_seq'::regclass);


--
-- Name: message id; Type: DEFAULT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message ALTER COLUMN id SET DEFAULT nextval('public.message_id_seq'::regclass);


--
-- Name: client client_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.client
    ADD CONSTRAINT client_pkey PRIMARY KEY (id);


--
-- Name: mailing mailing_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.mailing
    ADD CONSTRAINT mailing_pkey PRIMARY KEY (id);


--
-- Name: message message_mailing_id_client_id_key; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_mailing_id_client_id_key UNIQUE (mailing_id, client_id);


--
-- Name: message message_pkey; Type: CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_pkey PRIMARY KEY (id);


--
-- Name: message message_client_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_client_id_fkey FOREIGN KEY (client_id) REFERENCES public.client(id);


--
-- Name: message message_mailing_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: postgres
--

ALTER TABLE ONLY public.message
    ADD CONSTRAINT message_mailing_id_fkey FOREIGN KEY (mailing_id) REFERENCES public.mailing(id);


--
-- PostgreSQL database dump complete
--

