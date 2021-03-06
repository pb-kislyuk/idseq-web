# Configuration for alignment database for pipelines
# See also create_alignment_config.rake where configs are created.
class AlignmentConfig < ApplicationRecord
  has_many :pipeline_runs, dependent: :restrict_with_exception

  validates :name, presence: true, uniqueness: true, if: :mass_validation_enabled?
  validates :s3_nt_db_path, presence: true, if: :mass_validation_enabled?
  validates :s3_nt_loc_db_path, presence: true, if: :mass_validation_enabled?
  validates :s3_nr_db_path, presence: true, if: :mass_validation_enabled?
  validates :s3_nr_loc_db_path, presence: true, if: :mass_validation_enabled?
  validates :s3_lineage_path, presence: true, if: :mass_validation_enabled?
  validates :s3_accession2taxid_path, presence: true, if: :mass_validation_enabled?
  validates :s3_deuterostome_db_path, presence: true, if: :mass_validation_enabled?
  validates :s3_taxon_blacklist_path, presence: true, if: :mass_validation_enabled?
  validates :lineage_version, presence: true, numericality: { integer_only: true, greater_than: 0 }, if: -> { respond_to?(:lineage_version) && mass_validation_enabled? } # respond_to? for migrations

  # configuration for alignment database for pipelines
  #   set in SSM and loaded via chamber
  DEFAULT_NAME = ENV["ALIGNMENT_CONFIG_DEFAULT_NAME"]

  # Get the max lineage version from a set of alignment config ids.
  def self.max_lineage_version(alignment_config_ids)
    AlignmentConfig
      .select("lineage_version")
      .where(id: alignment_config_ids)
      .maximum(:lineage_version)
  end
end
