from config import engine
from models import *
from sqlalchemy import text

print("Creating tables...")
Base.metadata.create_all(bind=engine)
print("Done.")
print("Creating triggers...")

with engine.connect() as connection:
	connection.execute(text("""
		create or replace function check_cumulative_probability()
		returns trigger as $$
		declare cumulative_prob float;
		begin
			select sum(probability) + new.probability
			into cumulative_prob
			from ads
			where campaign_id = new.campaign_id;

			if cumulative_prob < 0 or cumulative_prob > 1 then
				raise exception 'Cumulative sum of probabilities is not between 0 and 1';
			end if;

			return new;
		end;
		$$ language plpgsql;

		create or replace trigger bound_probability
		before INSERT or UPDATE on ads
		for each row
		execute function check_cumulative_probability();
	"""))

	connection.execute(text("""
		create or replace function delete_old_interests()
		returns trigger as $$
		begin
			delete from interests
			where (user_id, tag_id) = (new.user_id, new.tag_id);
			return null;
		end;
		$$ language plpgsql;

		create or replace trigger bound_interest
		before UPDATE on interests
		for each row
		when (new.interest <= 0)
		execute function delete_old_interests();
	"""))
	connection.commit()

print("Done.")
